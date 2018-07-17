# -*- coding: utf-8 -*-

import requests
import typing
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from bs4 import BeautifulSoup

@dataclass
class SinglePost:
    title: str = field(default_factory=str)
    text: str = field(default_factory=str)

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


class MfdUserPostSource(DataSource):
    def __init__(self):
        super().__init__(lambda x: requests.get(self.url.format(id=x)).content)
        self.url = "http://lite.mfd.ru/forum/poster/posts/?id={id}"

    def check_update(self) -> Page:
        page_num = 0
        res = []
        for data in self.data_list:
            bs = BeautifulSoup(self.generator(data), "html.parser")
            title = [p.text.strip() for p in bs.select("h3.mfd-post-thread-subject > a")]
            posts = [p.text.strip() for p in bs.select("div.mfd-post-body-right")]
            page_num = int(bs.select_one("a.mfd-paginator-selected").text)

            if len(title) == len(posts) and len(title) > 0:
                for i in range(len(title)):
                    res.append(SinglePost(title[i], posts[i]))

        return Page(page_num, res)


class MfdUserCommentSource(DataSource):
    def __init__(self):
        super().__init__(lambda x: requests.get(self.url.format(id=x)).content)
        self.url = "http://lite.mfd.ru/forum/poster/comments/?id={id}"

    def check_update(self) -> Page:
        res = []
        page_num = 0
        for data in self.data_list:
            bs = BeautifulSoup(self.generator(data), "html.parser")
            title = [p.text.strip() for p in bs.select("h3.mfd-post-thread-subject > a")]
            posts = [p.text.strip() for p in bs.select("div.mfd-post-body-right")]
            page_num = int(bs.select_one("a.mfd-paginator-selected").text)

            if len(title) == len(posts) and len(title) > 0:
                for i in range(len(title)):
                    res.append(SinglePost(title[i], posts[i]))

        return Page(page_num, res)


class MfdForumThreadSource(DataSource):
    def __init__(self):
        super().__init__(lambda x: requests.get(self.url.format(id=x)).content)
        self.url = "http://lite.mfd.ru/forum/thread/?id={id}"

    def check_update(self) -> Page:
        res = []
        page_num = 0
        for data in self.data_list:
            bs = BeautifulSoup(self.generator(data), "html.parser")
            title = [p.text.strip() for p in bs.select("div.mfd-post-top-0 > a")]
            posts = [p.text.strip() for p in bs.select("div.mfd-post-body-right")]
            page_num = int(bs.select_one("a.mfd-paginator-selected").text)

            if len(title) == len(posts) and len(title) > 0:
                for i in range(len(title)):
                    res.append(SinglePost(title[i], posts[i]))

        return Page(page_num, res)


class AlenkaNews(AbstractSource):
    def __init__(self):
        super().__init__(lambda: requests.get(self.url).content)
        self.url = "https://alenka.capital"

    def check_update(self) -> Page:
        bs = BeautifulSoup(self.generator(), "html.parser")
        return Page(posts=[p.text.strip() for p in bs.select("h2.news__name > a")])


class AlenkaPost(AbstractSource):
    def __init__(self):
        super().__init__(lambda: requests.get(self.url).content)
        self.url = "https://alenka.capital"

    def check_update(self) -> Page:
        bs = BeautifulSoup(self.generator(), "html.parser")
        return Page(posts=[p.text.strip() for p in bs.select("h2.feed__text > a")])
