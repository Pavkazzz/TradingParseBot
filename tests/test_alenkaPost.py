# -*- coding: utf-8 -*-
import time
from unittest import TestCase
from sources import AlenkaPost, Page


class TestAlenkaNews(TestCase):
    def test_local_generator(self):
        alenka = AlenkaPost()
        with open("html/test_alenkaPage.html", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            alenka.set_generator(lambda: text)
        page: Page = alenka.check_update()
        self.assertEqual(len(page.posts), 10)
        self.assertEqual(page.posts[0].md, ("17.07.2018, 13:50\n"
                                            "\n"
                                            "[Психология торговли](https://alenka.capital/category/psihologiya_torgovli_604/)\n"
                                            "\n"
                                            "##  [Закрытия дивидендных гэпов 2015](https://alenka.capital/post/zakryitiya_dividendnyih_gepov_2015_39173/)"))

        self.assertEqual(page.posts[9].md, ("16.07.2018, 16:51\n"
                                            "\n"
                                            "[Обзоры секторов](https://alenka.capital/category/obzoryi_sektorov_31/)\n"
                                            "\n"
                                            "##  [Российские металлурги и промышленный цикл](https://alenka.capital/post/rossiyskie_metallurgi_i_promyishlennyiy_tsikl_39164/)"))

        for x in page.posts:
            self.assertNotEqual(len(x.md), 0)

    def test_online_generator(self):
        post = AlenkaPost()
        page: Page = post.check_update()
        self.assertGreater(len(page.posts), 0)
        for x in page.posts:
            self.assertNotEqual(len(x.md), 0)

    def test_cache(self):
        post = AlenkaPost()
        t = time.time()
        post.check_update()
        t_load = time.time()
        for _ in range(10):
            post.check_update()
        t_cache = time.time()
        self.assertLess(t_load - t, t_cache - t_load)
