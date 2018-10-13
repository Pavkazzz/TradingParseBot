# -*- coding: utf-8 -*-
import logging
import re
import typing
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from itertools import zip_longest
from typing import Tuple
from urllib.parse import quote

import fast_json
from aiohttp import ClientSession, TCPConnector, ClientResponse
from selectolax.parser import HTMLParser
from yarl import URL

from trading_bot import utils
from trading_bot.settings import alenka_url, chatbase_token


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


chatbase_redirect_url_with_a_http = '<a href="' + str(URL.build(
    scheme='https',
    host='chatbase.com',
    path='r',
    query={
        "api_key": chatbase_token,
        "platform": "Telegram",
    }
)) + "&url=http://"

chatbase_redirect_url_with_a_https = '<a href="' + str(URL.build(
    scheme='https',
    host='chatbase.com',
    path='r',
    query={
        "api_key": chatbase_token,
        "platform": "Telegram",
    }
)) + "&url=https://"

chatbase_redirect_url_no_base = '<a href="' + str(URL.build(
    scheme='https',
    host='chatbase.com',
    path='r',
    query={
        "api_key": chatbase_token,
        "platform": "Telegram",
    }
)) + "&url={baseurl}/"



def replace_url_for_chatbase(html, baseurl=None):
    # Это пиздец какая ебала
    # Значит делаем так:
    # 1. Сначала делаем замену урлов с http://
    # 2. Сначала делаем замену урлов с https://
    # 3. Потом делаем замену базовых
    resp = re.sub(r"(<a [^>]*href\s*=\s*['\"])(https://)", chatbase_redirect_url_with_a_https, html)
    resp = re.sub(r"(<a [^>]*href\s*=\s*['\"])(http://)", chatbase_redirect_url_with_a_http, resp)
    resp = re.sub(r"(<a [^>]*href\s*=\s*['\"])/", chatbase_redirect_url_no_base.format(baseurl=baseurl), resp)
    return resp


class AbstractSource(metaclass=ABCMeta):
    def __init__(self, url, caching_time: int = 60):
        self._url = url
        self._last_request = {}
        self._caching_time = timedelta(seconds=caching_time)
        self._connector = TCPConnector()
        self._last_time_request = datetime.min

    def update_cache(self, value):
        self._last_request[self._url] = value
        self._last_time_request = datetime.utcnow()

    async def session(self, custom_url=None, **format_url):

        url = self._url if not custom_url else custom_url

        if self._last_time_request + self._caching_time > datetime.utcnow() and url in self._last_request:
            logging.info('Not time for request url: %r', url)
            return self._last_request[url]

        async with ClientSession() as session:
            async with session.get(url.format(**format_url)) as r:  # type: ClientResponse
                body = await r.read()

        self.update_cache(body)
        return body

    @abstractmethod
    def check_update(self) -> Page:
        pass

    @staticmethod
    def pretty_text(html, baseurl) -> str:
        import html2text
        h = html2text.HTML2Text(baseurl=baseurl, bodywidth=34)
        # Небольшие изощрения с li
        html_to_parse = str(html).replace('<li', '<div').replace("</li>", "</div>")
        if '[' in html_to_parse and ']' in html_to_parse:
            html_to_parse = html_to_parse.replace('[', '{').replace(']', '}')

        html_to_parse = replace_url_for_chatbase(html_to_parse, baseurl)

        html_to_parse = utils.transform_emoji(html_to_parse)
        return h.handle(html_to_parse).strip()


class MfdSource(AbstractSource):
    def __init__(self, url, id_selector):
        super().__init__(url, 60 * 2)
        self.id_selector = id_selector

    async def check_update(self, data=None) -> Page:
        parser = HTMLParser(await self.session(id=data))
        thread = self.thread_selector(parser)
        user = [self.pretty_text(p.html, "http://mfd.ru") for p in parser.css("div.mfd-post-top-0 > a")]
        link = [self.pretty_text(p.html, "http://mfd.ru") for p in parser.css("div.mfd-post-top-1")]
        posts = [self.pretty_text(p.html, "http://mfd.ru") for p in parser.css("div.mfd-post-body-right")]
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
        return [self.pretty_text(p.text(), "http://mfd.ru") for p in parser.css("h3.mfd-post-thread-subject > a")]

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
        return [self.pretty_text(p.html, "http://mfd.ru") for p in bs.css("h3.mfd-post-thread-subject > a")]


class MfdForumThreadSource(MfdSource):
    def __init__(self):
        super().__init__("http://lite.mfd.ru/forum/thread/?id={id}", "button.mfd-button-attention")

    def thread_selector(self, bs):
        return [self.pretty_text(p.text(), "http://mfd.ru") for p in bs.css(".mfd-header > h1")]

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
                md=f"{post['post_date']}"
                f"\n\n"
                f"{utils.alert(post['post_alert'], False)}"
                f"[{post['post_name']}]({post['post_link']})",
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
                md=f"{post['post_date']}"
                f"\n\n"
                f"{utils.alert(post['post_alert'], True)}"
                f"[{post['cat_name']}]({post['cat_link']})\n\n"
                f"[{post['post_name']}]({post['post_link']})",
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
                md=self.pretty_text(post, self._url).strip(),
                title=self.title
            )
        ])
