# -*- coding: utf-8 -*-


import pytest

from trading_bot.sources import MfdUserPostSource

pytestmark = pytest.mark.asyncio


async def test_local_generator():
    res = (
        "| [Роберт СПБ](https://clck.ru/EZvsS) @ [17.07.2018 13:42](https://clck.ru/EZvta)\n"
        "|\n"
        "| \n"
        "| | [malishok](https://clck.ru/EZvFG) @ [17.07.2018 13:35](https://clck.ru/EZvtZ)\n"
        "| |  \n"
        "| |  есть) у меня она сложнее,\n"
        "| | смотрю ev/ebitda и p/e конечно, но\n"
        "| | расчитываю форвард на год+ и\n"
        "| | смотрю на менеджмент это для меня\n"
        "| | оч важно\n"
        "| | \n"
        "|  \n"
        "|  Но в EV/EBITDA и P/E\n"
        "| присутствует капитализация, что не\n"
        "| является объективные показателем.\n"
        "| Если не брать её во внимание, ты\n"
        "| на что больше смотришь, на\n"
        "| выручку, операционную прибыль или\n"
        "| чистую прибыль?\n"
        "\n"
        "смотри, я уже писал, для меня\n"
        "важнее менджмент и их работа, это\n"
        "немного более сложный анализ.  \n"
        "Если брать отчеты, то я смотрю\n"
        "операционку больше, чем ЧП ибо в\n"
        "ней много шлака, выручка зависит\n"
        "от компаний - в металлах смотрю, в\n"
        "киви нет, например. Тут компании\n"
        "разные")

    post = MfdUserPostSource()
    with open("html/test_mfdUserPostSourcePage.html", 'r', encoding="utf8") as html_page:
        post.update_cache('http://lite.mfd.ru/forum/poster/posts/?id=0', html_page.read())

    page = await post.check_update(0)
    assert len(page.posts) == 4
    assert page.posts[0].title == ("ФА и немного ТА\n"
                                   "[malishok](https://clck.ru/EZvFG)\n"
                                   "[17.07.2018 13:48](https://clck.ru/EZvsy)")
    assert page.posts[0].md == res
    for x in page.posts:
        assert len(x.title) != 0
        assert len(x.md) != 0
        assert x.id > 0


async def test_online_generator():
    post = MfdUserPostSource()
    page = await post.check_update(71921)
    assert len(page.posts) > 0
    for x in page.posts:
        assert len(x.title) > 0
        assert len(x.md) > 0
        assert x.id > 0


async def test_resolve():
    post = MfdUserPostSource()
    links = ["http://lite.mfd.ru/forum/poster/?id=71921",
             "http://lite.mfd.ru/forum/poster/posts/?id=71921",
             "http://lite.mfd.ru/forum/poster/comments/?id=71921",
             "http://lite.mfd.ru/forum/poster/rating/?id=71921",
             "http://lite.mfd.ru/forum/poster/chart/?id=71921"]
    for link in links:
        tid, name = await post.resolve_link(link)
        assert tid == 71921
        assert name == "malishok"


async def test_exact_find():
    post = MfdUserPostSource()
    user = "malishok"
    res = await post.find_user(user)
    assert len(res) == 1
    assert res[0][1] == user


async def test_exact_find2():
    post = MfdUserPostSource()
    user = "анонимный 666"
    res = await post.find_user(user)
    assert len(res) == 1
    assert res[0][1] == user


async def test_find():
    post = MfdUserPostSource()
    user = "анонимный"
    res = await post.find_user(user)
    assert len(res) > 0
