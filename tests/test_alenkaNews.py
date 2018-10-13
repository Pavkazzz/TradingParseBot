# -*- coding: utf-8 -*-

import pytest

from trading_bot.sources import AlenkaNews, Page

pytestmark = pytest.mark.asyncio


async def test_local_generator():
    alenka = AlenkaNews()
    with open("html/test_alenkaResponse.json", 'r', encoding="utf8") as json:
        alenka.update_cache(json.read())

    page: Page = await alenka.check_update()
    for post in page.posts:
        assert post.id > 0
        assert len(post.md) > 0

    assert len(page.posts) == 15
    assert page.posts[0].md == ("05.08.2018, 10:22\n"
                                "\n"
                                "[Индийская ONGC раскрыла суть претензий госкомпании к партнерам по проекту «Сахалин-1»](https://alenka.capital/post/indiyskaya_ongc_raskryila_sut_pretenziy_goskompanii_k_partneram_po_proektu_sahalin_1_39468/)")

    assert page.posts[-1].md == ("03.08.2018, 12:01\n"
                                 "\n"
                                 "[ОБЩИЙ ОБЪЕМ ПОКУПКИ МИНФИНОМ РФ ВАЛЮТЫ НА РЫНКЕ С 7 АВГУСТА ПО 6 СЕНТЯБРЯ БУДЕТ РЕКОРДНЫМ ](https://alenka.capital/post/obschiy_ob_em_pokupki_minfinom_rf_valyutyi_na_ryinke_s_7_avgusta_po_6_sentyabrya_budet_rekordnyim_39450/)")
