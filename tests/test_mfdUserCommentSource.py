# -*- coding: utf-8 -*-

import pytest

from trading_bot.sources import MfdUserCommentSource

pytestmark = pytest.mark.asyncio


async def test_local_generator():
    post = MfdUserCommentSource()
    with open("html/test_mfdUserCommentSourcePage.html", 'r', encoding="utf8") as html_page:
        post.update_cache(html_page.read())

    page = await post.check_update()
    assert len(page.posts) == 4
    assert page.posts[0].title == ("[{Блоги} Июль](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://lite.mfd.ru/blogs/posts/view/?id=37688)\n"
                                   "[malishok](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/poster/?id=71921)\n"
                                   "сегодня, 12:35")
    for x in page.posts:
        assert len(x.title) > 0
        assert len(x.md) > 0
        assert x.id > 0


async def test_online_generator():
    post = MfdUserCommentSource()
    page = await post.check_update(71921)
    assert len(page.posts) > 0
    for x in page.posts:
        assert len(x.title) > 0
        assert len(x.md) > 0
        assert x.id > 0
