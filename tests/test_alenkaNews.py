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
        self.assertEqual(len(page.posts), 14)
        self.assertEqual(page.posts[0].md, ("01.08.2018, 18:14\n"
                                            "\n"
                                            "[ГАЗПРОМ В ИЮЛЕ УВЕЛИЧИЛ ЭКСПОРТ ](https://alenka.capital/post/gazprom_v_iyule_uvelichil_eksport_39397/)"))

        self.assertEqual(page.posts[-1].md, ("01.08.2018, 11:01\n"
                                             "\n"
                                             "[Банкам по-прежнему выгоднее выдавать потребительские займы, чем кредитовать предприятия - Орешкин](https://alenka.capital/post/bankam_po_prejnemu_vyigodnee_vyidavat_potrebitelskie_zaymyi_chem_kreditovat_predpriyatiya_oreshkin_39376/)"))

        for x in page.posts:
            self.assertNotEqual(len(x.md), 0)

    def test_online_generator(self):
        post = AlenkaNews()
        page = post.check_update()
        self.assertGreater(len(page.posts), 0)
        for x in page.posts:
            self.assertNotEqual(len(x.md), 0)
