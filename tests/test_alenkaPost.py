# -*- coding: utf-8 -*-
import time
from unittest import TestCase
from sources import AlenkaPost, Page


class TestAlenkaNews(TestCase):
    def test_local_generator(self):
        alenka = AlenkaPost()
        with open("html/test_alenkaResponse.json", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            alenka.set_generator(lambda: text)
        page: Page = alenka.check_update()
        for post in page.posts:
            self.assertGreater(post.id, 0)
            self.assertGreater(len(post.md), 0)

        self.assertEqual(len(page.posts), 4)
        self.assertEqual(page.posts[0].md, ("04.08.2018, 12:23\n"
                                            "\n"
                                            "💡 [Стратегия](https://alenka.capital/category/strategiya_624/)\n"
                                            "\n"
                                            "[Как покупать \"сникерсы\"?](https://alenka.capital/post/kak_pokupat_snikersyi_39465/)"))

        self.assertEqual(page.posts[-1].md, ("03.08.2018, 11:37\n"
                                             "\n"
                                             "💡 [Сникерсы](https://alenka.capital/category/snikersyi_857/)\n"
                                             "\n"
                                             "[Tesla отчет за 2-й квартал 2018](https://alenka.capital/post/tesla_otchet_za_2_y_kvartal_2018_39423/)"))

    def test_online_generator(self):
        post = AlenkaPost()
        page: Page = post.check_update()
        self.assertGreater(len(page.posts), 0)
        for post in page.posts:
            self.assertGreater(post.id, 0)
            self.assertGreater(len(post.md), 0)

    def test_cache(self):
        post = AlenkaPost()
        t = time.time()
        post.check_update()
        t_load = time.time()
        for _ in range(10):
            post.check_update()
        t_cache = time.time()
        self.assertLess(t_load - t, t_cache - t_load)


