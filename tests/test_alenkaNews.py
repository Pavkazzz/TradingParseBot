# -*- coding: utf-8 -*-

from unittest import TestCase
from sources import AlenkaNews, Page


class TestAlenkaNews(TestCase):
    def test_local_generator(self):
        alenka = AlenkaNews()
        with open("html/test_alenkaResponse.json", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            alenka.set_generator(lambda: text)
        page: Page = alenka.check_update()
        self.assertEqual(len(page.posts), 15)
        self.assertEqual(page.posts[0].md, ("05.08.2018, 10:22\n"
                                            "\n"
                                            "[Индийская ONGC раскрыла суть претензий госкомпании к партнерам по проекту «Сахалин-1»](https://alenka.capital/post/indiyskaya_ongc_raskryila_sut_pretenziy_goskompanii_k_partneram_po_proektu_sahalin_1_39468/)"))

        self.assertEqual(page.posts[-1].md, ("03.08.2018, 12:01\n"
                                             "\n"
                                             "[ОБЩИЙ ОБЪЕМ ПОКУПКИ МИНФИНОМ РФ ВАЛЮТЫ НА РЫНКЕ С 7 АВГУСТА ПО 6 СЕНТЯБРЯ БУДЕТ РЕКОРДНЫМ ](https://alenka.capital/post/obschiy_ob_em_pokupki_minfinom_rf_valyutyi_na_ryinke_s_7_avgusta_po_6_sentyabrya_budet_rekordnyim_39450/)"))

        for x in page.posts:
            self.assertNotEqual(len(x.md), 0)

    def test_online_generator(self):
        post = AlenkaNews()
        page = post.check_update()
        self.assertGreater(len(page.posts), 0)
        for x in page.posts:
            self.assertNotEqual(len(x.md), 0)
