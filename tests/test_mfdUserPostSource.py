# -*- coding: utf-8 -*-

from unittest import TestCase
from sources import MfdUserPostSource


class TestUserMfdPostSource(TestCase):
    def test_local_generator(self):
        res = (
            "| [Роберт СПБ](http://mfd.ru/forum/poster/?id=84758) @ [17.07.2018 13:42](http://mfd.ru/forum/post/?id=14765308)\n"
            "|\n"
            "| \n"
            "| | [malishok](http://mfd.ru/forum/poster/?id=71921) @ [17.07.2018 13:35](http://mfd.ru/forum/post/?id=14765273)\n"
            "| |  \n"
            "| |  есть) у меня она сложнее, смотрю\n"
            "| | ev/ebitda и p/e конечно, но расчитываю\n"
            "| | форвард на год+ и смотрю на менеджмент\n"
            "| | это для меня оч важно\n"
            "| | \n"
            "|  \n"
            "|  Но в EV/EBITDA и P/E присутствует\n"
            "| капитализация, что не является\n"
            "| объективные показателем. Если не брать\n"
            "| её во внимание, ты на что больше\n"
            "| смотришь, на выручку, операционную\n"
            "| прибыль или чистую прибыль?\n"
            "\n"
            "смотри, я уже писал, для меня важнее\n"
            "менджмент и их работа, это немного более\n"
            "сложный анализ.  \n"
            "Если брать отчеты, то я смотрю\n"
            "операционку больше, чем ЧП ибо в ней\n"
            "много шлака, выручка зависит от компаний\n"
            "- в металлах смотрю, в киви нет,\n"
            "например. Тут компании разные")

        self.maxDiff = None
        post = MfdUserPostSource()
        with open("html/test_mfdUserPostSourcePage.html", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            post.set_generator(lambda x: text)
        post.add_data(71921)
        page = post.check_update()
        self.assertEqual(len(page.posts), 4)
        self.assertEqual(page.posts[0].title, ("ФА и немного ТА\n"
                                               "[malishok](http://mfd.ru/forum/poster/?id=71921)\n"
                                               "[17.07.2018 13:48](http://lite.mfd.ru/forum/post/?id=14765341)"))
        self.assertEqual(page.posts[0].md, res)
        for x in page.posts:
            self.assertNotEqual(len(x.title), 0)
            self.assertNotEqual(len(x.md), 0)

    def test_online_generator(self):
        post = MfdUserPostSource()
        post.add_data(71921)
        page = post.check_update()
        self.assertGreater(len(page.posts), 0)
        for x in page.posts:
            self.assertNotEqual(len(x.title), 0)
            self.assertNotEqual(len(x.md), 0)

    def test_resolve(self):
        post = MfdUserPostSource()
        links = ["http://lite.mfd.ru/forum/poster/?id=71921", "http://lite.mfd.ru/forum/poster/posts/?id=71921",
                 "http://lite.mfd.ru/forum/poster/comments/?id=71921",
                 "http://lite.mfd.ru/forum/poster/rating/?id=71921",
                 "http://lite.mfd.ru/forum/poster/chart/?id=71921"]
        for link in links:
            tid, name = post.resolve_link(link)
            self.assertEqual(tid, 71921)
            self.assertEqual(name, "malishok")

    def test_exact_find(self):
        post = MfdUserPostSource()
        user = "malishok"
        res = post.find_user(user)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][1], user)

    def test_exact_find2(self):
        post = MfdUserPostSource()
        user = "анонимный 666"
        res = post.find_user(user)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][1], user)

    def test_find(self):
        post = MfdUserPostSource()
        user = "анонимный"
        res = post.find_user(user)
        self.assertGreater(len(res), 0)
