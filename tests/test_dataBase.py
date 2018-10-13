import pytest
from trading_bot.database import DataBase
from trading_bot.sources import Page, SinglePost, MfdForumThreadSource

pytestmark = pytest.mark.asyncio


async def test_update():
    db = DataBase()
    cid = 9999
    post = SinglePost(title="123", md="qwe")
    res = db.update("alenka_news", Page(), cid)
    assert res == []
    res = db.update("alenka_news", Page(posts=[post]), cid)
    assert res == [SinglePost(title='123', md='qwe', id=0)]
    res = db.update("alenka_news", Page(posts=[post]), cid)
    assert res == []


async def test_check_all():
    db = DataBase()
    cid = 9999
    thread = MfdForumThreadSource()
    with open("html/test_mfdForumThreadSourcePage.html", encoding="utf8") as html_page:
        thread.update_cache(html_page.read())

    data = await thread.check_update()
    db.update("test", data, cid)
    for i in range(5):
        assert db.update("test", data, cid) == []
