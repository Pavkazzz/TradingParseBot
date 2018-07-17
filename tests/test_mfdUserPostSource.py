# -*- coding: utf-8 -*-

from unittest import TestCase
from sources import MfdUserPostSource

class TestUserMfdPostSource(TestCase):
    def test_local_generator(self):
        post = MfdUserPostSource()
        with open("html/test_mfdUserPostSourcePage.html", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            post.set_generator(lambda x: text)
        post.add_data(71921)
        page = post.check_update()
        self.assertEqual(len(page.posts), 4)
        self.assertEqual(page.posts[0].title, "ФА и немного ТА")
        self.assertEqual(page.num, 686)
        for x in page.posts:
            self.assertNotEqual(len(x.title), 0)
            self.assertNotEqual(len(x.text), 0)

    def test_online_generator(self):
        post = MfdUserPostSource()
        post.add_data(71921)
        page = post.check_update()
        self.assertGreater(len(page.posts), 0)
        self.assertGreater(page.num, 0)
        for x in page.posts:
            self.assertNotEqual(len(x.title), 0)
            self.assertNotEqual(len(x.text), 0)


