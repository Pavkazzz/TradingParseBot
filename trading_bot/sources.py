# -*- coding: utf-8 -*-

import typing
import ujson as json
import requests_cache
import requests
from typing import Tuple
from bs4 import BeautifulSoup
from trading_bot import utils
from urllib.parse import quote
from itertools import zip_longest
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from trading_bot.settings import alenka_url


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


class AbstractSource(metaclass=ABCMeta):
    def __init__(self, generator, time_cache=60):
        self.generator = generator
        self.time_cache = time_cache

    def set_generator(self, generator):
        self.generator = generator

    @property
    def session(self):
        return requests_cache.CachedSession(cache_name='data/cache', backend='sqlite', expire_after=self.time_cache)

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

        html_to_parse = utils.transform_emoji(html_to_parse)
        return h.handle(html_to_parse).strip()


class MfdSource(AbstractSource):
    def __init__(self, generator, id_selector):
        super().__init__(generator, 60 * 2)
        self.id_selector = id_selector

    def check_update(self, data=None) -> Page:
        bs = BeautifulSoup(self.generator(data), "html.parser")
        thread = self.thread_selector(bs)
        user = [self.pretty_text(p, "http://mfd.ru") for p in bs.select("div.mfd-post-top-0 > a")]
        link = [self.pretty_text(p, "http://mfd.ru") for p in bs.select("div.mfd-post-top-1")]
        posts = [self.pretty_text(p, "http://mfd.ru") for p in bs.select("div.mfd-post-body-right")]
        ids = [int(p.attrs['data-id']) for p in bs.select(self.id_selector)]

        if len(thread) > 0:
            tuple_title = tuple(zip_longest(thread, user, link, fillvalue=thread[0]))
            title = [f"{title[0]}\n{title[1]}\n{title[2]}" for title in tuple_title]
            return Page([SinglePost(title=data[0], md=data[1], id=data[2])
                         for data in zip(title, posts, ids)])

        return Page()

    @abstractmethod
    def thread_selector(self, bs):
        pass


class MfdUserPostSource(MfdSource):
    def __init__(self):
        super().__init__(lambda x: self.session.get(self.url.format(id=x)).content,
                         "button.mfd-button-attention")

        self.url = "http://lite.mfd.ru/forum/poster/posts/?id={id}"

    def thread_selector(self, bs):
        return [self.pretty_text(p.text, "http://mfd.ru") for p in bs.select("h3.mfd-post-thread-subject > a")]

    def resolve_link(self, url):
        bs = BeautifulSoup(self.session.get(url).content, "html.parser")
        name = bs.select_one("div.mfd-header h1").text.strip().split(' ')[-1]
        tid = int(bs.select_one("div.mfd-header div a").attrs['href'].split('?id=')[1])
        return tid, name

    def find_user(self, param) -> Tuple[Tuple[int, str, int, int]]:
        url = f"http://lite.mfd.ru/forum/users/?search={quote(param)}"
        bs = BeautifulSoup(self.session.get(url).content, "html.parser")
        ids = [int(user.next) for user in bs.select("tbody tr td.mfd-item-id")]
        names = [str(user.next.text) for user in bs.select("tbody tr td.mfd-item-nickname")]
        post_counts = [int(user.next.text) for user in bs.select("tbody tr td.mfd-item-postcount")]
        rating = [int(user.next.text) for user in bs.select("tbody tr td.mfd-item-rating")]

        users = tuple(zip(ids, names, post_counts, rating))
        active_users = tuple(filter(lambda x: x[2] > 0 and x[3] > 0, users))
        return active_users


class MfdUserCommentSource(MfdSource):
    def __init__(self):
        super().__init__(lambda x: self.session.get(self.url.format(id=x)).content,
                         "button.mfd-button-quote")
        self.url = "http://lite.mfd.ru/forum/poster/comments/?id={id}"

    def thread_selector(self, bs):
        return [self.pretty_text(p, "http://mfd.ru") for p in bs.select("h3.mfd-post-thread-subject > a")]


class MfdForumThreadSource(MfdSource):
    def __init__(self):
        super().__init__(lambda x: self.session.get(self.url.format(id=x)).content,
                         "button.mfd-button-attention")
        self.url = "http://lite.mfd.ru/forum/thread/?id={id}"

    def thread_selector(self, bs):
        return [self.pretty_text(p.text, "http://mfd.ru") for p in bs.select(".mfd-header > h1")]

    def resolve_link(self, url):
        bs = BeautifulSoup(self.session.get(url).content, "html.parser")
        tid = int(bs.select_one("a.mfd-link-dotted").attrs['href'].split('?threadId=')[1])
        name = bs.select_one("div.mfd-header").text.strip()
        return tid, name

    def find_thread(self, param):
        url = f"http://lite.mfd.ru/forum/search/?query=1+2+3+4+5+6+7+8+9+0+%D0%B0+%D0%B1+%D0%B2+%D0%B3+%D0%B4&method" \
              f"=Or&userQuery=&threadQuery={quote(param)}&from=&till= "
        bs = BeautifulSoup(self.session.get(url).content, "html.parser")
        title = [post.text for post in bs.select("h3.mfd-post-thread-subject > a")]
        title = list(set(title))
        if len(title) == 1:
            href = "http://lite.mfd.ru"
            href += bs.select_one("h3.mfd-post-thread-subject > a").attrs['href']
            tid, name = self.resolve_link(href)
            return title, tid, name
        return title, None, None


class AlenkaNews(AbstractSource):
    def __init__(self):
        super().__init__(lambda: requests.get(self.url).content)
        self.url = alenka_url

    def check_update(self) -> Page:
        title = "ALЁNKA CAPITAL"
        data = json.loads(self.generator())
        posts = list(filter(lambda x: x['cat_name'] == "Лента новостей", data))
        el = []
        for post in posts:
            el.append(SinglePost(md=f"{post['post_date']}\n\n"
                                    f"{utils.alert(post['post_alert'], False)}"
                                    f"[{post['post_name']}]({post['post_link']})",
                                 title=title,
                                 id=post['post_id']))

        return Page(el)


class AlenkaPost(AbstractSource):
    def __init__(self):
        super().__init__(lambda: requests.get(self.url).content)
        self.url = alenka_url

    def check_update(self) -> Page:
        title = "ALЁNKA CAPITAL"
        data = json.loads(self.generator())
        posts = list(filter(lambda x: x['cat_name'] != "Лента новостей", data))
        el = []
        for post in posts:
            el.append(SinglePost(md=f"{post['post_date']}\n\n"
                                    f"{utils.alert(post['post_alert'], True)}"
                                    f"[{post['cat_name']}]({post['cat_link']})\n\n"
                                    f"[{post['post_name']}]({post['post_link']})",
                                 title=title,
                                 id=post['post_id']))

        return Page(el)


class SmartLab(AbstractSource):
    def __init__(self):
        super().__init__(lambda: self.session.get(self.url).content, 60 * 60)
        self.url = "https://smart-lab.ru"

    def check_update(self) -> Page:
        bs = BeautifulSoup(self.generator(), "html.parser")
        title = "Smartlab топ 24 часа"
        post = bs.select_one("div.trt")
        return Page([SinglePost(md=self.pretty_text(post, self.url).strip(), title=title)])