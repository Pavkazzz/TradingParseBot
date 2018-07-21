from unittest import TestCase
from sources import MfdForumThreadSource


class TestMfdForumThreadSource(TestCase):
    def test_local_generator(self):
        thread = MfdForumThreadSource()
        with open("html/test_mfdForumThreadSourcePage.html", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            thread.set_generator(lambda x: text)
        thread.add_data(84424)
        page = thread.check_update()
        self.assertEqual(len(page.posts), 33)
        self.assertEqual(page.posts[0].title,
                         "[Спокойный Скрудж Макдак](http://mfd.ru/forum/poster/?id=88887)")
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
