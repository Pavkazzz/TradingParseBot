# -*- coding: utf-8 -*-
import pytest

from trading_bot.manager import Data
from trading_bot.sources import MfdUserPostSource, MfdForumThreadSource

pytestmark = pytest.mark.asyncio


async def test_mfd_user_post_comment_eq():
    post = MfdUserPostSource()
    thread = MfdForumThreadSource()

    with open("html/test_mfdUserPostEq.html", 'r', encoding="utf8") as html:
        post.update_cache("http://lite.mfd.ru/forum/poster/posts/?id=0", html.read())
    with open("html/test_mfdThreadEq.html", 'r', encoding="utf8") as html:
        thread.update_cache("http://lite.mfd.ru/forum/thread/?id=0", html.read())

    post_page = await post.check_update(0)
    thread_page = await thread.check_update(0)

    assert len(thread_page.posts) == 1
    assert len(post_page.posts) == 1
    assert post_page.posts[0].format() == thread_page.posts[0].format()
    assert post_page.posts[0].id == thread_page.posts[0].id


async def test_remove_duplicate():
    data = Data()
    data.mfd_user = ["one", "two", "one", "three", "one"]
    data.mfd_thread = ["Раз", "Два", "Раз", "Три", "Раз"]
    data.remove_duplicate()
    assert data.mfd_user == ["one", "two", "three"]
    assert data.mfd_thread == ["Раз", "Два", "Три"]
