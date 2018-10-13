# -*- coding: utf-8 -*-
import time

from trading_bot.sources import AlenkaPost, Page
import pytest

pytestmark = pytest.mark.asyncio


async def test_local_generator():
    alenka = AlenkaPost()
    with open("html/test_alenkaResponse.json", 'r', encoding="utf8") as json:
        alenka.update_cache(json.read())
    page: Page = await alenka.check_update()
    for post in page.posts:
        assert post.id > 0
        assert len(post.md) > 0

    assert len(page.posts) == 4
    assert page.posts[0].md == ("04.08.2018, 12:23\n"
                                "\n"
                                "💡 [Стратегия](https://alenka.capital/category/strategiya_624/)\n"
                                "\n"
                                "[Как покупать \"сникерсы\"?](https://alenka.capital/post/kak_pokupat_snikersyi_39465/)")

    assert page.posts[-1].md == ("03.08.2018, 11:37\n"
                                 "\n"
                                 "💡 [Сникерсы](https://alenka.capital/category/snikersyi_857/)\n"
                                 "\n"
                                 "[Tesla отчет за 2-й квартал 2018](https://alenka.capital/post/tesla_otchet_za_2_y_kvartal_2018_39423/)")
