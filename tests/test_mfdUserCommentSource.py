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
    assert page.posts[0].title == ("[{Блоги} Июль](http://lite.mfd.ru/blogs/posts/view/?id=37688)\n"
                                   "[malishok](http://mfd.ru/forum/poster/?id=71921)\n"
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
