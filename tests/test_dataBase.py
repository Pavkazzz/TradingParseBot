from unittest import TestCase

from database import DataBase
from sources import Page, SinglePost, MfdForumThreadSource


class TestDataBase(TestCase):
    def test_update(self):
        db = DataBase()
        post = SinglePost(title="123", md="qwe")
        res = db.update("alenka_news", Page())
        self.assertEqual(res, [])
        res = db.update("alenka_news", Page(posts=[post]))
        self.assertEqual(res, ['123\nqwe'])
        res = db.update("alenka_news", Page(posts=[post]))
        self.assertEqual(res, [])

    def test_check_all(self):
        db = DataBase()
        thread = MfdForumThreadSource()
        with open("html/test_mfdForumThreadSourcePage.html", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            thread.set_generator(lambda x: text)

        thread.add_data(84424)
        print(db.update("test", thread.check_update()))
        for i in range(5):
            print(db.update("test", thread.check_update()))
