# -*- coding: utf-8 -*-

from unittest import TestCase
from sources import MfdUserCommentSource


class TestMfdUserCommentSource(TestCase):
    def test_local_generator(self):
        post = MfdUserCommentSource()
        with open("html/test_mfdUserCommentSourcePage.html", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            post.set_generator(lambda x: text)

        page = post.check_update()
        self.assertEqual(len(page.posts), 4)
        self.assertEqual(page.posts[0].title, ("[{Блоги} Июль](http://lite.mfd.ru/blogs/posts/view/?id=37688)\n"
                                               "[malishok](http://mfd.ru/forum/poster/?id=71921)\n"
                                               "сегодня, 12:35"))
        for x in page.posts:
            self.assertNotEqual(len(x.title), 0)
            self.assertNotEqual(len(x.md), 0)
            self.assertGreater(x.id, 0)

    def test_online_generator(self):
        post = MfdUserCommentSource()
        page = post.check_update(71921)
        self.assertGreater(len(page.posts), 0)
        for x in page.posts:
            self.assertNotEqual(len(x.title), 0)
            self.assertNotEqual(len(x.md), 0)
            self.assertGreater(x.id, 0)
