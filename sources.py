from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class SinglePost:
    title: str
    text: str


class AbstractSource(metaclass=ABCMeta):
    def __init__(self):
        self.data_list = []

    def add_data(self, data):
        if self.data_list.count(data) == 0:
            self.data_list.append(data)

    def remove_data(self, data):
        try:
            self.data_list.remove(data)
        except ValueError:
            print("Ошибка удаления")

    @abstractmethod
    def check_update(self):
        pass


class MfdUserPostSource(AbstractSource):
    def __init__(self):
        super().__init__()
        self.url = "http://forum.mfd.ru/forum/poster/posts/?id={id}"
        self.generator = lambda x: requests.get(self.url.format(id=x)).content

    def set_generator(self, generator):
        self.generator = generator

    def check_update(self):
        res = []
        for data in self.data_list:
            bs = BeautifulSoup(self.generator(data), "html.parser")
            title = [p.text for p in bs.find_all("h3", {"class": "mfd-post-thread-subject"}, "a")]
            posts = [p.text for p in bs.find_all("div", {"class": "mfd-post-body-right"})]

            if len(title) == len(posts) and len(title) > 0:
                for i in range(len(title)):
                    res.append(SinglePost(title[i], posts[i]))

        return res


class MfdUserCommentSource(AbstractSource):
    def __init__(self):
        super().__init__()
        self.url = "http://forum.mfd.ru/forum/poster/comments/?id={id}"
        self.generator = lambda x: requests.get(self.url.format(id=x)).content

    def set_generator(self, generator):
        self.generator = generator

    def check_update(self):
        res = []
        for data in self.data_list:
            bs = BeautifulSoup(self.generator(data), "html.parser")
            title = [p.text for p in bs.find_all("h3", {"class": "mfd-post-thread-subject"}, "a")]
            posts = [p.text for p in bs.find_all("div", {"class": "mfd-post-body-right"})]

            if len(title) == len(posts) and len(title) > 0:
                for i in range(len(title)):
                    res.append(SinglePost(title[i], posts[i]))
        return res
