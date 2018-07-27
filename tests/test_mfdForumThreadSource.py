from unittest import TestCase
from sources import MfdForumThreadSource


class TestMfdForumThreadSource(TestCase):
    def test_local_generator(self):
        import sys
        sys.setrecursionlimit(20000)
        thread = MfdForumThreadSource()
        with open("html/test_mfdForumThreadSourcePage.html", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            thread.set_generator(lambda x: text)
        thread.add_data(84424)
        page = thread.check_update()
        self.assertEqual(len(page.posts), 33)
        self.assertEqual(page.posts[0].title,
                         ("ФА и немного ТА\n"
                          "[Спокойный Скрудж Макдак](http://mfd.ru/forum/poster/?id=88887)\n"
                          "[17.07.2018 12:02](http://lite.mfd.ru/forum/post/?id=14764606)"))
        for x in page.posts:
            self.assertNotEqual(len(x.title), 0)
            self.assertNotEqual(len(x.md), 0)

    def test_online_generator(self):
        post = MfdForumThreadSource()
        post.add_data(84424)
        page = post.check_update()
        self.assertGreater(len(page.posts), 0)
        for x in page.posts:
            self.assertNotEqual(len(x.title), 0)
            self.assertNotEqual(len(x.md), 0)

    def test_resolve(self):
        post = MfdForumThreadSource()
        links = ["http://lite.mfd.ru/forum/thread/?id=84424", "http://lite.mfd.ru/forum/post/?id=14792900"]
        for link in links:
            tid, name = post.resolve_link(link)
            self.assertEqual(tid, 84424)
            self.assertEqual(name, "ФА и немного ТА")

    def test_good_find(self):
        post = MfdForumThreadSource()
        res, tid, name = post.find_thread("фа")
        self.assertEqual(len(res), 1)
        self.assertTrue("ФА и немного ТА" in res)
        self.assertEqual(tid, 84424)
        self.assertEqual("ФА и немного ТА", name)

    def test_hard_find(self):
        post = MfdForumThreadSource()
        res = post.find_thread("та")
        self.assertGreater(len(res), 1)
