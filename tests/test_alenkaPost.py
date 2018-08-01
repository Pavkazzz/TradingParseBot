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
        self.assertEqual(len(page.posts), 6)
        self.assertEqual(page.posts[0].md, ("01.08.2018, 18:06\n"
                                            "\n"
                                            "[Кирилл Фомичев](https://alenka.capital/category/kirill_fomichev_67/)\n"
                                            "\n"
                                            "[ПАО «НГК «Славнефть» отчет за I полугодие 2018 МСФО](https://alenka.capital/post/pao_ngk_slavneft_otchet_za_i_polugodie_2018_msfo_39396/)"))

        self.assertEqual(page.posts[-1].md, ("01.08.2018, 11:11\n"
                                             "\n"
                                             "[Сникерсы](https://alenka.capital/category/snikersyi_857/)\n"
                                             "\n"
                                             "[Arcelor Mittal отчет за 2-й квартал 2018 года](https://alenka.capital/post/arcelor_mittal_otchet_za_2_y_kvartal_2018_goda_39372/)"))

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
