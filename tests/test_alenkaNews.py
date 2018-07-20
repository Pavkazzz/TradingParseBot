# -*- coding: utf-8 -*-

from unittest import TestCase
from sources import AlenkaNews, Page


class TestAlenkaNews(TestCase):
    def test_local_generator(self):
        alenka = AlenkaNews()
        with open("html/test_alenkaPage.html", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            alenka.set_generator(lambda: text)
        page: Page = alenka.check_update()
        self.assertEqual(len(page.posts), 20)
        self.assertEqual(page.posts[0].md, ("18:33\n"
                                            "\n"
                                            "##  [Vale во II квартале увеличил выпуск железной руды на 15%, производство никеля снизил на 3% ](https://alenka.capital/post/vale_vo_ii_kvartale_uvelichil_vyipusk_jeleznoy_rudyi_na_15_proizvodstvo_nikelya_snizil_na_3_39168/)"))

        self.assertEqual(page.posts[19].md,
                         "[1](https://alenka.capital/post/h5_i_magnit_dvigayut_figuryi_39017/?comment \"1 комментарий\")\n"
                         "\n"
                         "06:36\n"
                         "\n"
                         "##  [ Х5 и \"Магнит\" двигают фигуры](https://alenka.capital/post/h5_i_magnit_dvigayut_figuryi_39017/)")

        for x in page.posts:
            self.assertNotEqual(len(x.md), 0)

    def test_online_generator(self):
        post = AlenkaNews()
        page = post.check_update()
        self.assertGreater(len(page.posts), 0)
        for x in page.posts:
            self.assertNotEqual(len(x.md), 0)
