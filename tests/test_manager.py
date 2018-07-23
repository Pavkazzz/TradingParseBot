from unittest import TestCase
from manager import Manager
import random

class TestManager(TestCase):
    def test_start(self):
        manager = Manager()
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
        manager = Manager()
        chat_id = random.randint(0, 1000)
        manager.start(chat_id)
        manager.new_command(chat_id, Manager.ADD_ALENKA)
        manager.new_command(chat_id, f"/{Manager.ADD_MFD_USER} 71921")
        manager.new_command(chat_id, f"/{Manager.ADD_MFD_THREAD} 84424")
        manager.check_new(chat_id)