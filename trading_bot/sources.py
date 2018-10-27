# -*- coding: utf-8 -*-
import logging
import re
import typing
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import partial
from itertools import zip_longest
from typing import Tuple
from urllib.parse import quote

import fast_json
import html2text
import requests
from aiohttp import ClientSession, ClientResponse, ClientResponseError
from selectolax.parser import HTMLParser
from yarl import URL

from trading_bot import utils
from trading_bot.settings import alenka_url, chatbase_token

log = logging.getLogger(__name__)


@dataclass(unsafe_hash=True)
class SinglePost:
    title: str = field(default_factory=str)
    md: str = field(default_factory=str)
    id: int = field(default=0)

    def format(self) -> str:
        return f"{self.title}\n{self.md}"


@dataclass
class Page:
    posts: typing.List[SinglePost] = field(default_factory=list)


def get_chatbase_url(url):
    return str(URL.build(
        scheme='https',
        host='chatbase.com',
        path='r',
        query={
            "api_key": chatbase_token,
            "platform": "Telegram",
            "url": url
        }
    ))


def get_click_link_with_brackets(url):
    try:
        req_url = f'https://clck.ru/--?url={quote(get_chatbase_url(url), encoding="ascii")}'
    except UnicodeEncodeError:
        log.exception('Failed to encode url %r', url)
        req_url = url
    return f"({requests.get(req_url).text})"


class MarkdownFormatter:

    def __init__(self, base_url):
        self.base_url = base_url

    def make_request(self, match):
        url = match.group(0)[1:-1]
        return get_click_link_with_brackets(url)

    def convert_links(self, markdown):
        # noinspection PyTypeChecker
        return re.sub(r"(\(https?://\S+\))", partial(self.make_request), markdown)

    def parse_markdown(self, html, width=34) -> str:
        h = html2text.HTML2Text(baseurl=self.base_url, bodywidth=width)
        # Небольшие изощрения с li
        html_to_parse = str(html).replace('<li', '<div').replace("</li>", "</div>")
        if '[' in html_to_parse and ']' in html_to_parse:
            html_to_parse = html_to_parse.replace('[', '{').replace(']', '}')

        html_to_parse = utils.transform_emoji(html_to_parse)
        return self.convert_links(h.handle(html_to_parse).strip())


class AbstractSource(metaclass=ABCMeta):
    def __init__(self, url, caching_time: int = 60, formatter_url=None):
        self._url = url
        self._last_request = {}
        self._caching_time = timedelta(seconds=caching_time)
        self._last_time_request = datetime.min
        self._formatter = MarkdownFormatter(formatter_url or self._url)

    def update_cache(self, url, value):
        self._last_request[url] = value
        self._last_time_request = datetime.utcnow()

    async def session(self, custom_url=None, **format_url):
        url = self._url.format(**format_url) if not custom_url else custom_url

        if self._last_time_request + self._caching_time > datetime.utcnow() and url in list(self._last_request.keys()):
            log.info('Not time for request url: %r', url)
            return self._last_request[url]

        try:
            async with ClientSession(raise_for_status=True) as session:
                async with session.get(url) as r:  # type: ClientResponse
                    body = await r.read()
        except ClientResponseError:
            log.exception('Error')
            body = """<html></html>"""

        self.update_cache(url, body)
        return body

    @abstractmethod
    def check_update(self, *args) -> Page:
        pass

    def pretty_text(self, html):
        return self._formatter.parse_markdown(html)


class MfdSource(AbstractSource):
    def __init__(self, url, id_selector):
        super().__init__(url, 60 * 2, formatter_url="http://mfd.ru")
        self.id_selector = id_selector

    async def check_update(self, data) -> Page:
        html = await self.session(id=data)
        parser = HTMLParser(html)
        thread = self.thread_selector(parser)
        user = [self.pretty_text(p.html) for p in parser.css("div.mfd-post-top-0 > a")]
        link = [self.pretty_text(p.html) for p in parser.css("div.mfd-post-top-1")]
        posts = [self.pretty_text(p.html) for p in parser.css("div.mfd-post-body-right")]
        ids = [int(p.attributes['data-id']) for p in parser.css(self.id_selector)]

        if len(thread) > 0:
            tuple_title = tuple(zip_longest(thread, user, link, fillvalue=thread[0]))
            title = [f"{title[0]}\n{title[1]}\n{title[2]}" for title in tuple_title]
            return Page([SinglePost(title=data[0], md=data[1], id=data[2])
                         for data in zip(title, posts, ids)])

        return Page()

    @abstractmethod
    def thread_selector(self, parser):
        pass


class MfdUserPostSource(MfdSource):
    def __init__(self):
        super().__init__("http://lite.mfd.ru/forum/poster/posts/?id={id}", "button.mfd-button-attention")

    def thread_selector(self, parser):
        return [self.pretty_text(p.text()) for p in parser.css("h3.mfd-post-thread-subject > a")]

    async def resolve_link(self, url):
        parser = HTMLParser(await self.session(custom_url=url))
        name = parser.css_first("div.mfd-header h1").text().strip().split(' ')[-1]
        tid = int(parser.css_first("div.mfd-header div a").attributes['href'].split('?id=')[1])
        return tid, name

    async def find_user(self, param) -> Tuple[Tuple[int, str, int, int]]:
        url = f"http://lite.mfd.ru/forum/users/?search={quote(param)}"
        parser = HTMLParser(await self.session(custom_url=url))
        ids = [int(user.text()) for user in parser.css("tbody tr td.mfd-item-id")]
        names = [str(user.text()) for user in parser.css("tbody tr td.mfd-item-nickname")]
        post_counts = [int(user.text()) for user in parser.css("tbody tr td.mfd-item-postcount")]
        rating = [int(user.text()) for user in parser.css("tbody tr td.mfd-item-rating")]

        users = tuple(zip(ids, names, post_counts, rating))
        return tuple(filter(lambda x: x[2] > 0 and x[3] > 0, users))


class MfdUserCommentSource(MfdSource):
    def __init__(self):
        super().__init__("http://lite.mfd.ru/forum/poster/comments/?id={id}", "button.mfd-button-quote")

    def thread_selector(self, bs):
        return [self.pretty_text(p.html) for p in bs.css("h3.mfd-post-thread-subject > a")]


class MfdForumThreadSource(MfdSource):
    def __init__(self):
        super().__init__("http://lite.mfd.ru/forum/thread/?id={id}", "button.mfd-button-attention")

    def thread_selector(self, bs):
        return [self.pretty_text(p.text()) for p in bs.css(".mfd-header > h1")]

    async def resolve_link(self, url):
        parser = HTMLParser(await self.session(custom_url=url))
        tid = int(parser.css_first("a.mfd-link-dotted").attributes['href'].split('?threadId=')[1])
        name = parser.css_first("div.mfd-header").text().strip()
        return tid, name

    async def find_thread(self, param):
        url = f"http://lite.mfd.ru/forum/search/?query=1+2+3+4+5+6+7+8+9+0+%D0%B0+%D0%B1+%D0%B2+%D0%B3+%D0%B4&method" \
              f"=Or&userQuery=&threadQuery={quote(param)}&from=&till="
        bs = HTMLParser(await self.session(custom_url=url))
        title = [post.text() for post in bs.css("h3.mfd-post-thread-subject > a")]
        title = list(set(title))
        if len(title) == 1:
            href = f"http://lite.mfd.ru{bs.css_first('h3.mfd-post-thread-subject > a').attributes['href']}"
            tid, name = await self.resolve_link(href)
            return title, tid, name
        return title, None, None


class AlenkaNews(AbstractSource):
    def __init__(self):
        super().__init__(alenka_url)
        self.title = "ALЁNKA CAPITAL"

    async def check_update(self) -> Page:
        data = fast_json.loads(await self.session())

        return Page([
            SinglePost(
                md=(f"{post['post_date']}"
                    f"\n\n"
                    f"{utils.alert(post['post_alert'], False)}"
                    f"[{post['post_name']}]{get_click_link_with_brackets(post['post_link'])}"),
                title=self.title,
                id=post['post_id'])
            for post in [item for item in data if item['cat_name'] == "Лента новостей"]
        ])


class AlenkaPost(AbstractSource):
    def __init__(self):
        super().__init__(alenka_url)
        self.title = "ALЁNKA CAPITAL"

    async def check_update(self) -> Page:
        data = fast_json.loads(await self.session())

        return Page([
            SinglePost(
                md=(f"{post['post_date']}"
                    f"\n\n"
                    f"{utils.alert(post['post_alert'], True)}"
                    f"[{post['cat_name']}]{get_click_link_with_brackets(post['cat_link'])}\n\n"
                    f"[{post['post_name']}]{get_click_link_with_brackets(post['post_link'])}"),
                title=self.title,
                id=post['post_id'])
            for post in [item for item in data if item['cat_name'] != "Лента новостей"]
        ])


class SmartLab(AbstractSource):
    def __init__(self):
        super().__init__("https://smart-lab.ru")
        self.title = "Smartlab топ 24 часа"

    async def check_update(self) -> Page:
        parser = HTMLParser(await self.session(), "html.parser")
        post = parser.css_first("div.trt").html
        return Page([
            SinglePost(
                md=self.pretty_text(post).strip(),
                title=self.title
            )
        ])
