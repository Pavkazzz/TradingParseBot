# -*- coding: utf-8 -*-

from unittest import TestCase
from sources import MfdUserCommentSource

class TestMfdUserCommentSource(TestCase):
    def test_local_generator(self):
        post = MfdUserCommentSource()
        with open("test_mfdCommentSourcePage.html", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            post.set_generator(lambda x: text)
        post.add_data(71921)
        posts = post.check_update()
        self.assertEqual(len(posts), 3)
        self.assertEqual(posts[0].title, "[Блоги] Июль")
        for x in posts:
            self.assertNotEqual(len(x.title), 0)
            self.assertNotEqual(len(x.text), 0)

    def test_online_generator(self):
        post = MfdUserCommentSource()
        post.add_data(71921)
        posts = post.check_update()
        self.assertGreater(len(posts), 0)
        for x in posts:
            self.assertNotEqual(len(x.title), 0)
            self.assertNotEqual(len(x.text), 0)
