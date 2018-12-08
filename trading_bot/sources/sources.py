# -*- coding: utf-8 -*-
import logging
import os
import re
import typing
from abc import ABCMeta, abstractmethod
from asyncio import gather
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import partial, reduce
from itertools import zip_longest
from typing import Tuple
from urllib.parse import quote

import fast_json
import html2text
from aiohttp import ClientSession, ClientResponseError, TCPConnector
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


class MarkdownFormatter:

    def __init__(self, base_url, disable_short=False):
        self.disable_short = disable_short
        self.base_url = base_url
        self.matcher = {}
        self.re = re.compile(r"(\(https?://\S+\))")
        self.connector = TCPConnector()

    def __del__(self):
        self.connector.close()

    async def get_click_link(self, url) -> typing.Tuple[str, str]:
        if self.disable_short or '@' in url:
            return url, url
        try:
            req_url = f'https://clck.ru/--?url={quote(get_chatbase_url(url), encoding="ascii")}'
        except UnicodeEncodeError:
            log.exception('Failed to encode url %r', url)
            req_url = url

        async with ClientSession(
            raise_for_status=True,
            connector=self.connector,
            connector_owner=False
        ) as session:
            async with session.get(req_url) as r:  # type: ClientResponse
                res = await r.text()
        return url, res

    def collect_matches(self, match: typing.Match[str]):
        self.matcher[match.group(0)[1:-1]] = ""

    async def convert_links(self, markdown: str) -> str:
        self.matcher = {}
        # noinspection PyTypeChecker
        self.re.sub(partial(self.collect_matches), markdown)
        tasks = [self.get_click_link(url) for url in self.matcher.keys()]
        res = await gather(*tasks)
        return reduce(lambda md, b: md.replace(f'({b[0]})', f'({b[1]})'), res, markdown)

    async def parse_markdown(self, html, width=269, max_length=4096) -> str:
        h = html2text.HTML2Text(baseurl=self.base_url, bodywidth=width)
        # Небольшие изощрения с li
        html_to_parse = str(html).replace('<li', '<div').replace("</li>", "</div>")
        if '[' in html_to_parse and ']' in html_to_parse:
            html_to_parse = html_to_parse.replace('[', '{').replace(']', '}')

        html_to_parse.replace('lite.mfd.ru', 'forum.mfd.ru')

        html_to_parse = utils.transform_emoji(html_to_parse)
        md = await self.convert_links(h.handle(html_to_parse).strip())
        if len(md) > max_length:
            md = f'{md[:max_length - 4]}...'
        return md


class AbstractSource(metaclass=ABCMeta):
    def __init__(self, url, caching_time: int = 60, formatter_url=None):
        self._url = url
        self._last_request = {}
        self._caching_time = timedelta(seconds=caching_time)
        self._last_time_request = datetime.min
        disable_short = os.environ.get('APP_DISABLE_SHORT', '0') == '1'
        self._formatter = MarkdownFormatter(formatter_url or self._url, disable_short)

    def update_cache(self, url, value):
        self._last_request[url] = value
        self._last_time_request = datetime.utcnow()

    async def session(self, custom_url=None, **format_url):
        url = self._url.format(**format_url) if not custom_url else custom_url

        if self._last_time_request + self._caching_time > datetime.utcnow() and url in list(self._last_request.keys()):
            log.info('Not time for request url: %r', url)
            return self._last_request[url]

        log.info('Make request %r', url)
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

    async def pretty_text(self, html):
        return await self._formatter.parse_markdown(html)


class MfdSource(AbstractSource):
    def __init__(self, url, id_selector):
        super().__init__(url, 60 * 2, formatter_url="http://mfd.ru")
        self.id_selector = id_selector

    async def check_update(self, data) -> Page:
        html = await self.session(id=data)
        parser = HTMLParser(html)
        thread = await self.thread_selector(parser)
        user = [await self.pretty_text(p.html) for p in parser.css("div.mfd-post-top-0 > a")]
        link = [await self.pretty_text(p.html) for p in parser.css("div.mfd-post-top-1")]
        posts = [await self.pretty_text(p.html) for p in parser.css("div.mfd-post-body-right")]
        ids = [int(p.attributes['data-id']) for p in parser.css(self.id_selector)]

        if len(thread) > 0:
            tuple_title = tuple(zip_longest(thread, user, link, fillvalue=thread[0]))
            title = [f"{title[0]}\n{title[1]}\n{title[2]}" for title in tuple_title]
            return Page([SinglePost(title=data[0], md=data[1], id=data[2])
                         for data in zip(title, posts, ids)])

        return Page()

    @abstractmethod
    async def thread_selector(self, parser):
        pass


class MfdUserPostSource(MfdSource):
    def __init__(self):
        super().__init__("http://lite.mfd.ru/forum/poster/posts/?id={id}", "button.mfd-button-attention")

    async def thread_selector(self, parser):
        return [await self.pretty_text(p.text()) for p in parser.css("h3.mfd-post-thread-subject > a")]

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

    async def thread_selector(self, bs):
        return [await self.pretty_text(p.html) for p in bs.css("h3.mfd-post-thread-subject > a")]


class MfdForumThreadSource(MfdSource):
    def __init__(self):
        super().__init__("http://lite.mfd.ru/forum/thread/?id={id}", "button.mfd-button-attention")

    async def thread_selector(self, bs):
        return [await self.pretty_text(p.text()) for p in bs.css(".mfd-header > h1")]

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
        super().__init__(alenka_url, caching_time=30)
        self.title = "ALЁNKA CAPITAL"

    async def check_update(self) -> Page:
        data = fast_json.loads(await self.session())

        return Page([
            SinglePost(
                md=(f"{post['post_date']}"
                    f"\n\n"
                    f"{utils.alert(post['post_alert'], False)}"
                    f"[{post['post_name']}]({(await self._formatter.get_click_link(post['post_link']))[1]})"),
                title=self.title,
                id=post['post_id'])
            for post in [item for item in data if item['cat_name'] == "Лента новостей"]
        ])


class AlenkaPost(AbstractSource):
    def __init__(self):
        super().__init__(alenka_url, caching_time=30)
        self.title = "ALЁNKA CAPITAL"

    async def check_update(self) -> Page:
        data = fast_json.loads(await self.session())

        return Page([
            SinglePost(
                md=(f"{post['post_date']}"
                    f"\n\n"
                    f"{utils.alert(post['post_alert'], True)}"
                    f"[{post['cat_name']}]({(await self._formatter.get_click_link(post['cat_link']))[1]})\n\n"
                    f"[{post['post_name']}]({(await self._formatter.get_click_link(post['post_link']))[1]})"),
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
                md=(await self.pretty_text(post)).strip(),
                title=self.title
            )
        ])
