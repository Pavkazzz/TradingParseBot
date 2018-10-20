# -*- coding: utf-8 -*-

from trading_bot.settings import alenka_url
from trading_bot.sources import AlenkaNews, Page


async def test_local_generator():
    alenka = AlenkaNews()
    with open("html/test_alenkaResponse.json", 'r', encoding="utf8") as json:
        alenka.update_cache(alenka_url, json.read())

    page: Page = await alenka.check_update()
    for post in page.posts:
        assert post.id > 0
        assert len(post.md) > 0

    assert len(page.posts) == 15
    assert page.posts[0].md == ("05.08.2018, 10:22\n"
                                "\n"
                                "[Индийская ONGC раскрыла суть претензий госкомпании к партнерам по проекту «Сахалин-1»](https://clck.ru/EZvEM)")

    assert page.posts[-1].md == ("03.08.2018, 12:01\n"
                                 "\n"
                                 "[ОБЩИЙ ОБЪЕМ ПОКУПКИ МИНФИНОМ РФ ВАЛЮТЫ НА РЫНКЕ С 7 АВГУСТА ПО 6 СЕНТЯБРЯ БУДЕТ РЕКОРДНЫМ ](https://clck.ru/EZvEc)")
