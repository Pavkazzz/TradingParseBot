from unittest import TestCase
from manager import Manager
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
        manager.new_command(chat_id, f"{Manager.ADD_MFD_USER} {user_id}")
        self.assertEqual(manager.settings(chat_id).mfd_user, [user_id])
        manager.new_command(chat_id, f"{Manager.REMOVE_MFD_USER} {user_id}")
        self.assertEqual(manager.settings(chat_id).mfd_user, [])

        thread_id = random.randint(0, 10000)
        manager.new_command(chat_id, f"{Manager.ADD_MFD_THREAD} {thread_id}")
        self.assertEqual(manager.settings(chat_id).mfd_thread, [thread_id])
        manager.new_command(chat_id, f"{Manager.REMOVE_MFD_THREAD} {thread_id}")
        self.assertEqual(manager.settings(chat_id).mfd_thread, [])

    def test_me(self):
        manager = Manager(clear_start=True)
        chat_id = random.randint(0, 1000)
        manager.start(chat_id)
        manager.new_command(chat_id, Manager.ADD_ALENKA)
        manager.new_command(chat_id, f"/{Manager.ADD_MFD_USER} 71921")
        manager.new_command(chat_id, f"/{Manager.ADD_MFD_THREAD} 84424")
        manager.check_new(chat_id)

    def test_all(self):
        self.maxDiff = None
        manager = Manager(clear_start=True)
        n = 10
        chats_id = [random.randint(i*n, i*n+n) for i in range(n)]
        for chat in chats_id:
            manager.start(chat)
            manager.new_command(chat, Manager.ADD_ALENKA)

        res = tuple([post for post in manager.check_all()])

        self.assertEqual(len(res), n)
        prev_chat, prev_data = res[0]
        for new_chat, new_data in res[1:]:
            self.assertNotEqual(prev_chat, new_chat)
            self.assertEqual(prev_data, new_data)
            prev_chat, prev_data = new_chat, new_data
