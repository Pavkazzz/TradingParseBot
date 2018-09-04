from unittest import TestCase
from trading_bot.manager import Manager, SingleData
from trading_bot.sources import SinglePost
import random


class TestManager(TestCase):
    def test_start(self):
        manager = Manager(clear_start=True)
        chat_id = random.randint(0, 1000)
        manager.start(chat_id)
        self.assertEqual(manager.settings(chat_id).alenka, False)
        manager.new_command(chat_id, Manager.ADD_ALENKA)
        self.assertEqual(manager.settings(chat_id).alenka, True)
        manager.new_command(chat_id, Manager.REMOVE_ALENKA)
        self.assertEqual(manager.settings(chat_id).alenka, False)

        user_id = random.randint(0, 10000)
        user_string = "Название пользователя"
        manager.new_command(chat_id, Manager.ADD_MFD_USER, SingleData(user_id, user_string))
        self.assertEqual(manager.settings(chat_id).mfd_user, [SingleData(user_id, user_string)])
        manager.new_command(chat_id, Manager.REMOVE_MFD_USER, SingleData(user_id, user_string))
        self.assertEqual(manager.settings(chat_id).mfd_user, [])

        thread_id = random.randint(0, 10000)
        thread_string = "Название треда"
        manager.new_command(chat_id, Manager.ADD_MFD_THREAD, SingleData(thread_id, thread_string))
        self.assertEqual(manager.settings(chat_id).mfd_thread, [SingleData(thread_id, thread_string)])
        manager.new_command(chat_id, Manager.REMOVE_MFD_THREAD, SingleData(thread_id, thread_string))
        self.assertEqual(manager.settings(chat_id).mfd_thread, [])

    def test_me(self):
        manager = Manager(clear_start=True)
        chat_id = random.randint(0, 1000)
        manager.start(chat_id)
        manager.new_command(chat_id, Manager.ADD_ALENKA)
        manager.new_command(chat_id, Manager.ADD_MFD_USER, SingleData(71921, "malishok"))
        manager.new_command(chat_id, Manager.ADD_MFD_THREAD, SingleData(84424, "ФА и немного ТА"))
        manager.check_new(chat_id)

    def test_all(self):
        self.maxDiff = None
        manager = Manager(clear_start=True)
        n = 10
        chats_id = [random.randint(i * n + 1, i * n + n) for i in range(n)]
        for chat in chats_id:
            manager.start(chat)
            manager.new_command(chat, Manager.ADD_ALENKA)

        res = tuple([post for post in manager.check_new_all()])

        self.assertEqual(len(res), n)
        prev_chat, prev_data = res[0]
        for new_chat, new_data in res[1:]:
            self.assertNotEqual(prev_chat, new_chat)
            self.assertEqual(prev_data, new_data)
            prev_chat, prev_data = new_chat, new_data

    def test_some_user(self):
        manager = Manager(clear_start=True)
        chats_id = random.randint(0, 999)
        manager.start(chats_id)
        manager.new_command(chats_id, Manager.ADD_MFD_USER, SingleData(71921, "malishok"))
        manager.new_command(chats_id, Manager.ADD_MFD_USER, SingleData(96540, "VVT5"))
        res1 = [post for post in manager.check_new_all()]
        res2 = [post for post in manager.check_new_all()]
        res3 = [post for post in manager.check_new_all()]

        self.assertEqual(res1[0][1], [])
        self.assertEqual(res2[0][1], [])
        self.assertEqual(res3[0][1], [])

    def test_alenka_unsubscr(self):
        manager = Manager(clear_start=True)
        with open("html/test_alenkaResponse.json", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            manager.config_sources("alenka_news", lambda: text)

        n = 10
        chats_id = [random.randint(i * n + 1, i * n + n) for i in range(n)]
        for chat in chats_id:
            manager.start(chat)
            if chat % 2:
                manager.new_command(chat, Manager.ADD_ALENKA)
            if chat % 3:
                manager.new_command(chat, Manager.ADD_MFD_USER, SingleData(id=random.randint(0, 100), name=str(chat)))
            if chat % 5:
                manager.new_command(chat, Manager.ADD_MFD_THREAD, SingleData(id=random.randint(0, 100), name=str(chat)))

        for user, post in manager.check_new_all():
            self.assertEqual(post, [])

        with open("html/test_alenkaResponseWithNewData.json", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            manager.config_sources("alenka_news", lambda: text)

        res = ("ALЁNKA CAPITAL\n"
               "05.08.2018, 10:25\n"
               "\n"
               "[Media Markt начал ликвидацию ассортимента перед уходом из России](https://alenka.capital/post/media_markt_nachal_likvidatsiyu_assortimenta_pered_uhodom_iz_rossii_39469/)")

        for user, post in manager.check_new_all():
            if user % 2:
                self.assertEqual(len(post), 1)
                self.assertEqual(post[0][0].format(), res)
            else:
                self.assertEqual(post, [])


        for user, post in manager.check_new_all():
            self.assertEqual(post, [])


    def test_delete(self):
        m = Manager(clear_start=True)
        cid = random.randint(0, 100)
        m.start(cid)
        m.new_command(cid, Manager.ADD_ALENKA)
        self.assertEqual(m.settings(cid).alenka, True)
        m.stop(cid)
        self.assertEqual(m.settings(cid).alenka, False)


    def test_alenka_editing(self):
        manager = Manager(clear_start=True)
        with open("html/test_alenkaResponse.json", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            manager.config_sources("alenka_news", lambda: text)

        chats_id = random.randint(0, 100)
        manager.start(chats_id)
        _, data = manager.new_command(chats_id, Manager.ADD_ALENKA)

        for post in data:
            manager.set_message_id(message_id=random.randint(0, 1000), chat_id=chats_id, post_id=post.id)

        for user, post in manager.check_new_all():
            self.assertEqual(post, [])

        with open("html/test_alenkaResponseEditing.json", 'r', encoding="utf8") as html_page:
            text = html_page.read()
            manager.config_sources("alenka_news", lambda: text)

        for user, posts in manager.check_new_all():
            post: SinglePost
            for post, message_id in posts:
                self.assertGreater(message_id, 0)
                self.assertGreater(len(post.format()), 0)


        for user, post in manager.check_new_all():
            self.assertEqual(post, [])