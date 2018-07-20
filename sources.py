# -*- coding: utf-8 -*-

import requests
import typing
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from bs4 import BeautifulSoup


@dataclass
class SinglePost:
    title: str = field(default_factory=str)
    md: str = field(default_factory=str)

    def format(self) -> str:
        return self.title + "\n" + self.md


@dataclass
class Page:
    num: int = field(default=0)
    posts: typing.List[SinglePost] = field(default_factory=list)


class AbstractSource(metaclass=ABCMeta):
    def __init__(self, generator):
        self.generator = generator

    def set_generator(self, generator):
        self.generator = generator

    @abstractmethod
    def check_update(self) -> Page:
        pass

    def pretty_text(self, html, baseurl) -> str:
        import html2text
        h = html2text.HTML2Text(baseurl=baseurl, bodywidth=40)
        # Небольшие изощрения с li
        return h.handle(str(html).replace('<li', '<div').replace("</li>", "</div>")).strip()


class DataSource(AbstractSource):
    @abstractmethod
    def check_update(self) -> Page:
        pass

    def __init__(self, generator):
        super().__init__(generator)
        self.data_list = []

    def add_data(self, data):
        if self.data_list.count(data) == 0:
            self.data_list.append(data)

    def remove_data(self, data):
        try:
            self.data_list.remove(data)
        except ValueError:
            print("Ошибка удаления")


class MfdSource(DataSource):
    def __init__(self, generator, title_selector):
        super().__init__(generator)
        self.title_selector = title_selector

    def check_update(self) -> Page:
        page_num = 0
        res = []
        for data in self.data_list:
            bs = BeautifulSoup(self.generator(data), "html.parser")
            title = [self.pretty_text(p, "http://mfd.ru") for p in bs.select(self.title_selector)]
            posts = [self.pretty_text(p, "http://mfd.ru") for p in bs.select("div.mfd-post-body-right")]
            page_num = int(bs.select_one("a.mfd-paginator-selected").text)

            if len(title) == len(posts) and len(title) > 0:
                for i in range(len(title)):
                    res.append(SinglePost(title[i], posts[i]))

        return Page(page_num, res)


class MfdUserPostSource(MfdSource):
    def __init__(self, data=None):
        super().__init__(lambda x: requests.get(self.url.format(id=x)).content, "h3.mfd-post-thread-subject > a")
        self.url = "http://lite.mfd.ru/forum/poster/posts/?id={id}"
        if data is not None:
            self.add_data(data)


class MfdUserCommentSource(MfdSource):
    def __init__(self, data=None):
        super().__init__(lambda x: requests.get(self.url.format(id=x)).content, "h3.mfd-post-thread-subject > a")
        self.url = "http://lite.mfd.ru/forum/poster/comments/?id={id}"
        if data is not None:
            self.add_data(data)


class MfdForumThreadSource(MfdSource):
    def __init__(self, data=None):
        super().__init__(lambda x: requests.get(self.url.format(id=x)).content, "div.mfd-post-top-0 > a")
        self.url = "http://lite.mfd.ru/forum/thread/?id={id}"
        if data is not None:
            self.add_data(data)


class AlenkaNews(AbstractSource):
    def __init__(self):
        super().__init__(lambda: requests.get(self.url).content)
        self.url = "https://alenka.capital"

    def check_update(self) -> Page:
        bs = BeautifulSoup(self.generator(), "html.parser")
        title = "ALЁNKA CAPITAL News: "
        el = [SinglePost(md=self.pretty_text(p, self.url).strip(), title=title) for p in bs.select("li.news__item")]
        return Page(posts=el)


class AlenkaPost(AbstractSource):
    def __init__(self):
        super().__init__(lambda: requests.get(self.url).content)
        self.url = "https://alenka.capital"

    def check_update(self) -> Page:
        bs = BeautifulSoup(self.generator(), "html.parser")
        title = "ALЁNKA CAPITAL Post: "
        el = [SinglePost(md=self.pretty_text(p, self.url).strip(), title=title) for p in bs.select("div.feed__content")]
        return Page(posts=el)
