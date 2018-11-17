# -*- coding: utf-8 -*-
from trading_bot.settings import alenka_url
from trading_bot.sources.sources import AlenkaPost, Page


async def test_alenka_post_local_generator():
    alenka = AlenkaPost()
    with open("html/test_alenkaResponse.json", 'r', encoding="utf8") as json:
        alenka.update_cache(alenka_url, json.read())
    page: Page = await alenka.check_update()
    for post in page.posts:
        assert post.id > 0
        assert len(post.md) > 0

    assert len(page.posts) == 4
    assert page.posts[0].md == ("04.08.2018, 12:23\n"
                                "\n"
                                "💡 [Стратегия](https://clck.ru/EZvEd)\n"
                                "\n"
                                "[Как покупать \"сникерсы\"?](https://clck.ru/EZvEe)")

    assert page.posts[-1].md == ("03.08.2018, 11:37\n"
                                 "\n"
                                 "💡 [Сникерсы](https://clck.ru/EZvEf)\n"
                                 "\n"
                                 "[Tesla отчет за 2-й квартал 2018](https://clck.ru/EZvEk)")
