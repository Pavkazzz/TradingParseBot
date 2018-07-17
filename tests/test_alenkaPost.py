# -*- coding: utf-8 -*-

from unittest import TestCase
from sources import AlenkaPost

class TestAlenkaNews(TestCase):
    def test_local_generator(self):
        alenka = AlenkaPost()
        with open("html/test_alenkaPage.html", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            alenka.set_generator(lambda: text)
        page = alenka.check_update()
        self.assertEqual(len(page.posts), 10)
        self.assertEqual(page.posts[0], "Закрытия дивидендных гэпов 2015")
        self.assertEqual(page.posts[9], "Российские металлурги и промышленный цикл")

        for x in page.posts:
            self.assertNotEqual(len(x), 0)

    def test_online_generator(self):
        post = AlenkaPost()
        page = post.check_update()
        self.assertGreater(len(page.posts), 0)
        for x in page.posts:
            self.assertNotEqual(len(x), 0)
