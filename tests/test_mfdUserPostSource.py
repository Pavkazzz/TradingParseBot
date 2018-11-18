# -*- coding: utf-8 -*-


import pytest

from trading_bot.sources.sources import MfdUserPostSource

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


async def test_doka():
    post = MfdUserPostSource()
    html = """<h3 class="mfd-post-thread-subject"><a href="/forum/post/?id=15318902" rel="nofollow" title="Перейти к сообщению">МРСК Центра и Приволжья (МРСК ЦП, MRKP)</a></h3><div class="mfd-post-top"><div class="mfd-post-top-0" id="15318902"><a class="mfd-poster-link" href="/forum/poster/?id=62543" rel="nofollow" title="ID: 62543">ДОКА</a></div><div class="mfd-post-top-1"><a class="mfd-post-link" href="http://lite.mfd.ru/forum/post/?id=15318902" rel="nofollow" title="Ссылка на это сообщение">29.10.2018 07:50</a></div><div class="mfd-post-top-4"><button class="mfd-button-quote" data-id="15318902" name="quotePost" title="Цитировать" type="button"> </button></div><div class="mfd-post-top-2"><span id="mfdPostRating15318902">&nbsp;</span></div><div class="mfd-post-top-3 mfd-post-top-3-disabled"><form><label class="mfd-post-rate--1"><input data-id="15318902" data-status="1" data-vote="-1" name="ratePost" type="radio">−1</label><label class="mfd-post-rate-0" style="display: none;"><input data-id="15318902" data-status="1" data-vote="0" name="ratePost" type="radio">0</label><label class="mfd-post-rate-1"><input data-id="15318902" data-status="1" data-vote="1" name="ratePost" type="radio">+1</label></form></div><div class="mfd-clear"></div></div><table><tbody><tr><td class="mfd-post-body-left-container"><div class="mfd-post-body-left"><div class="mfdPosterInfoShort"><div class="mfd-poster-info-rating mfd-icon-profile-star"><a href="/forum/poster/rating/?id=62543" rel="nofollow" title="Детализация рейтинга (43397)">43K</a></div><div class="mfd-poster-info-icons"><a class="mfd-icon-profile-hat-4" href="/forum/poster/forecasts/?id=62543" rel="nofollow" title="465 место в рейтинге прогнозов"></a></div></div></div></td><td class="mfd-post-body-right-container"><div class="mfd-post-body-right"><div><blockquote class="mfd-quote-15318897"><div class="mfd-quote-info"><a href="/forum/poster/?id=70074" rel="nofollow">loket</a> @ <a href="/forum/post/?id=15318897" rel="nofollow">29.10.2018 07:45</a></div><blockquote class="mfd-quote-15318886"><div class="mfd-quote-info"><a href="/forum/poster/?id=62543" rel="nofollow">ДОКА</a> @ <a href="/forum/post/?id=15318886" rel="nofollow">29.10.2018 07:35</a></div><div class="mfd-quote-text">Вчера кальвадос последний перегонял. Крепкость такая ,что думаю газонокосилку просто разнесло бы. Даже прикуривать рядом боюсь...</div></blockquote><div class="mfd-quote-text">газонокосилка тоже на кальвадосе работает??</div></blockquote><div class="mfd-quote-text">Думаю ещё как будет. Но у меня электрическая. Смысла не вижу в этих бензиновых машинках. Пила тоже электрическая.</div></div><button class="mfd-button-attention" data-id="15318902" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button></div></td></tr></tbody></table>"""
    post.update_cache('http://lite.mfd.ru/forum/poster/posts/?id=62543', html)
    res = await post.check_update(62543)
    assert res.posts[0].title == """МРСК Центра и Приволжья (МРСК ЦП,
MRKP)
[ДОКА](https://clck.ru/Ea2xg)
[29.10.2018 07:50](https://clck.ru/EcUNm)"""
    assert res.posts[0].md == """| [loket](https://clck.ru/EcUNp) @ [29.10.2018 07:45](https://clck.ru/EcUNq)
|
| 
| | [ДОКА](https://clck.ru/Ea2xg) @ [29.10.2018 07:35](https://clck.ru/EcUNr)
| |  
| |  Вчера кальвадос последний
| | перегонял. Крепкость такая ,что
| | думаю газонокосилку просто
| | разнесло бы. Даже прикуривать
| | рядом боюсь...
| | 
|  
|  газонокосилка тоже на
| кальвадосе работает??

Думаю ещё как будет. Но у меня
электрическая. Смысла не вижу в
этих бензиновых машинках. Пила
тоже электрическая."""
