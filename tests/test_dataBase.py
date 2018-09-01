from unittest import TestCase

from database import DataBase
from sources import Page, SinglePost, MfdForumThreadSource


class TestDataBase(TestCase):
    def test_update(self):
        db = DataBase()
        cid = 9999
        post = SinglePost(title="123", md="qwe")
        res = db.update("alenka_news", Page(), cid)
        self.assertEqual(res, [])
        res = db.update("alenka_news", Page(posts=[post]), cid)
        self.assertEqual(res, [SinglePost(title='123', md='qwe', id=0)])
        res = db.update("alenka_news", Page(posts=[post]), cid)
        self.assertEqual(res, [])

    def test_check_all(self):
        self.maxDiff = None
        db = DataBase()
        cid = 9999
        thread = MfdForumThreadSource()
        with open("html/test_mfdForumThreadSourcePage.html", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            thread.set_generator(lambda x: text)

        db.update("test", thread.check_update(), cid)
        for i in range(5):
            self.assertEqual(db.update("test", thread.check_update(), cid), [])
