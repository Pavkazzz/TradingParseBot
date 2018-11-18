import pytest

from trading_bot.sources.sources import SmartLab

pytestmark = pytest.mark.asyncio


async def test_local_generator():
    sl = SmartLab()
    with open("html/test_smartLab.html", "r", encoding="utf8") as html_page:
        text = html_page.read()
        sl.update_cache("https://smart-lab.ru", text)

    page = await sl.check_update()
    res = (
        "+320 (283) [Ситуация на текущий момент](https://clck.ru/EZwKc)\n"
        "\n"
        "+223 (97) [Мост на Сахалин](https://clck.ru/EZwKd)\n"
        "\n"
        "+186 (22) [Три стадии бедности](https://clck.ru/EZwKe)\n"
        "\n"
        "+157 (67) [Какой мост нужен на Сахалин?](https://clck.ru/EZwKf)\n"
        "\n"
        "+150 (27) [Про деньги](https://clck.ru/EZwKg)\n"
        "\n"
        "+150 (23) [Размещение ОФЗ + RGBI + Объём ОФЗ](https://clck.ru/EZwKh)\n"
        "\n"
        '+136 (23) ["Утренний звонок". Биржевой рассказ. Пролог.](https://clck.ru/EZwKj)\n'
        "\n"
        "+115 (32) [Запасы нефти в США: -6,1 мб, добыча: +0 тб/д](https://clck.ru/EZwKk)\n"
        "\n"
        "+104 (61) [Рассказ о моей торговле](https://clck.ru/EZwKn)\n"
        "\n"
        "+101 (0) [Рубль: usdrub - все пристегнулись? ... в 100тыс500 раз?!](https://clck.ru/EZwKo)"
    )

    assert len(page.posts) == 1
    assert page.posts[0].md == res
