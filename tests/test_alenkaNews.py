# -*- coding: utf-8 -*-

from unittest import TestCase
from sources import AlenkaNews


class TestAlenkaNews(TestCase):
    def test_local_generator(self):
        alenka = AlenkaNews()
        with open("html/test_alenkaPage.html", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            alenka.set_generator(lambda: text)
        page = alenka.check_update()
        self.assertEqual(len(page.posts), 20)
        self.assertEqual(page.posts[0], "Vale во II квартале увеличил выпуск железной руды на 15%, производство никеля "
                                        "снизил на 3%")
        self.assertEqual(page.posts[19], "Х5 и \"Магнит\" двигают фигуры")

        for x in page.posts:
            self.assertNotEqual(len(x), 0)

    def test_online_generator(self):
        post = AlenkaNews()
        page = post.check_update()
        self.assertGreater(len(page.posts), 0)
        for x in page.posts:
            self.assertNotEqual(len(x), 0)
