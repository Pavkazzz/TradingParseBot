from unittest import TestCase
from trading_bot.sources import SmartLab


class TestSmartLab(TestCase):

    def test_local_generator(self):
        sl = SmartLab()
        with open("html/test_smartLab.html", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            sl.set_generator(lambda: text)
        page = sl.check_update()
        res = ("+320 (283) [Ситуация на текущий момент](https://smart-lab.ru/blog/484064.php)\n"
               "\n"
               "+223 (97) [Мост на Сахалин](https://smart-lab.ru/blog/483969.php)\n"
               "\n"
               "+186 (22) [Три стадии бедности](https://smart-lab.ru/blog/483954.php)\n"
               "\n"
               "+157 (67) [Какой мост нужен на Сахалин?](https://smart-lab.ru/blog/484000.php)\n"
               "\n"
               "+150 (27) [Про деньги](https://smart-lab.ru/blog/484080.php)\n"
               "\n"
               "+150 (23) [Размещение ОФЗ + RGBI + Объём ОФЗ](https://smart-lab.ru/blog/483985.php)\n"
               "\n"
               "+136 (23) [\"Утренний звонок\". Биржевой рассказ. Пролог.](https://smart-lab.ru/blog/484054.php)\n"
               "\n"
               "+115 (32) [Запасы нефти в США: -6,1 мб, добыча: +0 тб/д](https://smart-lab.ru/blog/483979.php)\n"
               "\n"
               "+104 (61) [Рассказ о моей торговле](https://smart-lab.ru/blog/484071.php)\n"
               "\n"
               "+101 (0) [Рубль: usdrub - все пристегнулись? ... в 100тыс500 раз?!](https://smart-lab.ru/blog/484068.php)")

        self.assertEqual(len(page.posts), 1)
        self.assertEqual(page.posts[0].md, res)

    def test_online_generator(self):
        sl = SmartLab()
        page = sl.check_update()
        self.assertEqual(len(page.posts), 1)
