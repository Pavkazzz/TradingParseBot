import random

import pytest

from trading_bot.manager import Manager, SingleData
from trading_bot.settings import alenka_url

pytestmark = pytest.mark.asyncio


async def test_start():
    manager = Manager(clear_start=True)
    chat_id = random.randint(0, 1000)
    manager.start(chat_id, "tests")
    assert not manager.settings(chat_id).alenka
    await manager.new_command(chat_id, Manager.ADD_ALENKA)
    assert manager.settings(chat_id).alenka
    await manager.new_command(chat_id, Manager.REMOVE_ALENKA)
    assert not manager.settings(chat_id).alenka

    user_id = random.randint(0, 10000)
    user_string = "Название пользователя"
    await manager.new_command(chat_id, Manager.ADD_MFD_USER,
                              SingleData(user_id, user_string))
    assert manager.settings(chat_id).mfd_user == [
        SingleData(user_id, user_string)]
    await manager.new_command(chat_id, Manager.REMOVE_MFD_USER,
                              SingleData(user_id, user_string))
    assert manager.settings(chat_id).mfd_user == []

    thread_id = random.randint(0, 10000)
    thread_string = "Название треда"
    await manager.new_command(chat_id, Manager.ADD_MFD_THREAD,
                              SingleData(thread_id, thread_string))
    assert manager.settings(chat_id).mfd_thread == [
        SingleData(thread_id, thread_string)]
    await manager.new_command(chat_id, Manager.REMOVE_MFD_THREAD,
                              SingleData(thread_id, thread_string))
    assert manager.settings(chat_id).mfd_thread == []


async def test_me():
    manager = Manager(clear_start=True)
    chat_id = random.randint(0, 1000)
    manager.start(chat_id, "tests")
    await manager.new_command(chat_id, Manager.ADD_ALENKA)
    await manager.new_command(chat_id, Manager.ADD_MFD_USER,
                              SingleData(71921, "malishok"))
    await manager.new_command(chat_id, Manager.ADD_MFD_THREAD,
                              SingleData(84424, "ФА и немного ТА"))
    await manager.check_new(chat_id)


async def test_all():
    manager = Manager(clear_start=True)
    n = 10
    chats_id = [random.randint(i * n + 1, i * n + n) for i in range(n)]
    for chat_id in chats_id:
        manager.start(chat_id, "tests")
        await manager.new_command(chat_id, Manager.ADD_ALENKA)

    res = tuple([post async for post in manager.check_new_all()])

    assert len(res) == n
    prev_chat, prev_data = res[0]
    for new_chat, new_data in res[1:]:
        assert prev_chat != new_chat
        assert prev_data == new_data
        prev_chat, prev_data = new_chat, new_data


async def test_some_user():
    manager = Manager(clear_start=True)
    chats_id = random.randint(0, 999)
    manager.start(chats_id, "tests")
    await manager.new_command(chats_id, Manager.ADD_MFD_USER,
                              SingleData(71921, "malishok"))
    await manager.new_command(chats_id, Manager.ADD_MFD_USER,
                              SingleData(96540, "VVT5"))
    res = [
        [post async for post in manager.check_new_all()],
        [post async for post in manager.check_new_all()],
        [post async for post in manager.check_new_all()],
    ]

    for r in res:
        assert r[0][1] == []


async def test_alenka_unsubscr():
    manager = Manager(clear_start=True)
    with open("html/test_alenkaResponse.json", "r", encoding="utf8") as html:
        await manager.config_sources("alenka_news", alenka_url, html.read())

    n = 10
    chats_id = [random.randint(i * n + 1, i * n + n) for i in range(n)]
    for chat in chats_id:
        manager.start(chat, "tests")
        if chat % 2:
            await manager.new_command(chat, Manager.ADD_ALENKA)
        if chat % 3:
            await manager.new_command(chat, Manager.ADD_MFD_USER,
                                      SingleData(id=random.randint(0, 100),
                                                 name=str(chat)))
        if chat % 5:
            await manager.new_command(
                chat, Manager.ADD_MFD_THREAD,
                SingleData(id=random.randint(0, 100), name=str(chat))
            )

    async for user, post in manager.check_new_all():
        assert post == []

    with open("html/test_alenkaResponseWithNewData.json", "r",
              encoding="utf8") as html:
        await manager.config_sources("alenka_news", alenka_url, html.read())

    res = (
        "ALЁNKA CAPITAL\n"
        "05.08.2018, 10:25\n"
        "\n"
        "[Media Markt начал ликвидацию ассортимента перед уходом из России](https://alenka.capital/post/media_markt_nachal_likvidatsiyu_assortimenta_pered_uhodom_iz_rossii_39469/)"
    )

    async for user, post in manager.check_new_all():
        if user % 2:
            assert len(post) == 1
            assert post[0][0].format() == res
        else:
            assert post == []

    async for user, post in manager.check_new_all():
        assert post == []


async def test_delete():
    m = Manager(clear_start=True)
    cid = random.randint(0, 100)
    m.start(cid, "tests")
    await m.new_command(cid, Manager.ADD_ALENKA)
    assert m.settings(cid).alenka
    m.stop(cid)
    assert not m.settings(cid).alenka


async def test_alenka_editing():
    manager = Manager(clear_start=True)
    with open("html/test_alenkaResponse.json", "r", encoding="utf8") as html:
        await manager.config_sources("alenka_news", alenka_url, html.read())

    chats_id = random.randint(0, 100)
    manager.start(chats_id, "tests")
    _, data = await manager.new_command(chats_id, Manager.ADD_ALENKA)

    for post in data:
        manager.set_sended_id(message_id=random.randint(0, 1000),
                              chat_id=chats_id, post_id=post.id)

    async for user, post in manager.check_new_all():
        assert post == []

        with open("html/test_alenkaResponseEditing.json", "r",
                  encoding="utf8") as html:
            await manager.config_sources("alenka_news", alenka_url, html.read())

        async for nuser, nposts in manager.check_new_all():
            for npost, nmessage_id in nposts:
                assert nmessage_id > 0
                assert len(npost.format()) > 0

        async for user, post in manager.check_new_all():
            assert post == []
