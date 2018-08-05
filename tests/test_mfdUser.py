# -*- coding: utf-8 -*-

from unittest import TestCase
from sources import MfdUserPostSource, MfdForumThreadSource


class TestMfdUser(TestCase):
    def test_mfd_user_post_comment_eq(self):
        post = MfdUserPostSource()
        thread = MfdForumThreadSource()

        with open("html/test_mfdUserPostEq.html", 'r', encoding="utf8") as html:
            text = html.read()
            post.set_generator(lambda x: text)
        post_page = post.check_update()

        with open("html/test_mfdThreadEq.html", 'r', encoding="utf8") as html:
            text = html.read()
            thread.set_generator(lambda x: text)

        thread_page = thread.check_update()

        self.assertEqual(len(thread_page.posts), 1)
        self.assertEqual(len(post_page.posts), 1)
        self.assertEqual(post_page.posts[0].format(), thread_page.posts[0].format())
