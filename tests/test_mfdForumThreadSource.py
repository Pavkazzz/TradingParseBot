# -*- coding: utf-8 -*-
import pytest

from trading_bot.sources import MfdForumThreadSource

pytestmark = pytest.mark.asyncio


async def test_local_generator():
    thread = MfdForumThreadSource()
    with open("html/test_mfdForumThreadSourcePage.html", 'r', encoding="utf8") as html:
        thread.update_cache(html.read())

    page = await thread.check_update()
    assert len(page.posts) == 33
    assert page.posts[0].title == ("ФА и немного ТА\n"
                                   "[Спокойный Скрудж Макдак](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/poster/?id=88887)\n"
                                   "[17.07.2018 12:02](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://lite.mfd.ru/forum/post/?id=14764606)")

    for x in page.posts:
        assert len(x.title) > 0
        assert len(x.md) > 0
        assert x.id > 0


async def test_online_generator():
    post = MfdForumThreadSource()
    page = await post.check_update(84424)
    assert len(page.posts) > 0
    for x in page.posts:
        assert len(x.title) > 0
        assert len(x.md) > 0
        assert x.id > 0


async def test_resolve():
    post = MfdForumThreadSource()
    links = ["http://lite.mfd.ru/forum/thread/?id=84424", "http://lite.mfd.ru/forum/post/?id=14792900"]
    for link in links:
        tid, name = await post.resolve_link(link)
        assert tid == 84424
        assert name == "ФА и немного ТА"


async def test_good_find():
    post = MfdForumThreadSource()
    res, tid, name = await post.find_thread("фа")
    assert len(res) == 1
    assert "ФА и немного ТА" in res
    assert tid == 84424
    assert "ФА и немного ТА" == name


async def test_hard_find():
    post = MfdForumThreadSource()
    res = await post.find_thread("та")
    assert len(res) > 1


async def test_akula_post():
    html = """
    <div class="mfd-header" style="clear: none;">
    <h1>Московская Биржа (MOEX)</h1>
    <div></div>
    </div>
    <div class="mfd-post-top"><div class="mfd-post-top-0" id="14853474"><a class="mfd-poster-link" href="/forum/poster/?id=91582" rel="nofollow" title="ID: 91582">Акул*O®aCool</a></div><div class="mfd-post-top-1"><a class="mfd-post-link" href="http://forum.mfd.ru/forum/post/?id=14853474" rel="nofollow" title="Ссылка на это сообщение">04.08.2018 14:42</a></div><div class="mfd-post-top-4"><button class="mfd-button-quote" data-id="14853474" name="quotePost" title="Цитировать" type="button"> </button></div><div class="mfd-post-top-2"><span class="u" id="mfdPostRating14853474">1</span><div class="mfd-post-ratingdetails" style="display: none;"><table><tbody><tr><td><a href="/forum/poster/?id=99856" rel="nofollow">Фон Дон КаскЪ</a></td><td>+</td></tr></tbody></table></div></div><div class="mfd-post-top-3 mfd-post-top-3-disabled"><form><label class="mfd-post-rate--1"><input data-id="14853474" data-status="1" data-vote="-1" name="ratePost" type="radio">−1</label><label class="mfd-post-rate-0" style="display: none;"><input data-id="14853474" data-status="1" data-vote="0" name="ratePost" type="radio">0</label><label class="mfd-post-rate-1"><input data-id="14853474" data-status="1" data-vote="1" name="ratePost" type="radio">+1</label></form></div><div class="mfd-clear"></div></div><table><tbody><tr><td class="mfd-post-body-left-container"><div class="mfd-post-body-left"><div class="mfd-post-avatar"><a href="/forum/poster/?id=91582" rel="nofollow" title="ID: 91582"><img alt="" src="http://forum.mfd.ru/forum/user/91582/avatar.gif"></a></div><div class="mfdPosterInfoShort"><div class="mfd-poster-info-rating mfd-icon-profile-star"><a href="/forum/poster/rating/?id=91582" rel="nofollow" title="Детализация рейтинга (3263)">3263</a></div><div class="mfd-poster-info-icons"><a class="mfd-icon-profile-hat-4" href="/forum/poster/forecasts/?id=91582" rel="nofollow" title="409 место в рейтинге прогнозов"></a></div></div></div></td><td class="mfd-post-body-right-container"><div class="mfd-post-body-right"><div><div class="mfd-quote-text">Верните доктора верховцего!)))</div></div><button class="mfd-button-attention" data-id="14853474" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button></div></td></tr></tbody></table>"""

    res = ("Московская Биржа (MOEX)\n"
           "[Акул*O®aCool](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/poster/?id=91582)\n"
           "[04.08.2018 14:42](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://forum.mfd.ru/forum/post/?id=14853474)\n"
           "Верните доктора верховцего!)))")

    post = MfdForumThreadSource()
    post.update_cache(html)
    text = await post.check_update()
    assert len(text.posts) == 1
    assert text.posts[0].format() == res
