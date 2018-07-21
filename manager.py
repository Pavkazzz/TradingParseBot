# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from database import DataBase
import sources
import typing
import sys


@dataclass
class Data:
    mfd_user: typing.List[int] = field(default_factory=list)
    mfd_thread: typing.List[int] = field(default_factory=list)
    alenka: bool = field(default=False)


class Manager:
    db: DataBase
    ADD_ALENKA = "add_alenka"  # Включить новости с аленки
    REMOVE_ALENKA = "remove_alenka"  # Выключить новости с аленки
    ADD_MFD_USER = "add_mfd_user"  # + id - Добавить mfd пользователя по id
    REMOVE_MFD_USER = "remove_mfd_user"  # + id - Удалить mfd пользователя по id
    ADD_MFD_THREAD = "add_mfd_thread"  # + id - Добавить mfd форум по id
    REMOVE_MFD_THREAD = "remove_mfd_tread"  # + id - Удалить mfd форум по id

    def __init__(self):
        self.db = DataBase()
        self.users_subscription = self.db.load_user_data()

    def start(self, chat_id):
        if chat_id not in self.users_subscription:
            self.users_subscription[chat_id] = Data()

    def new_command(self, chat_id, text) -> str:
        res: str = ""
        try:
            if self.ADD_ALENKA in text:
                self.users_subscription[chat_id].alenka = True
                res = "Теперь вы подписаны на https://alenka.capital"
            if self.REMOVE_ALENKA in text:
                self.users_subscription[chat_id].alenka = False
                res = "Теперь вы отписаны от новостей с https://alenka.capital"
            if self.ADD_MFD_USER in text:
                user_id = int(text.split(self.ADD_MFD_USER)[1])
                self.users_subscription[chat_id].mfd_user.append(user_id)

            if self.REMOVE_MFD_USER in text:
                user_id = int(text.split(self.REMOVE_MFD_USER)[1])
                self.users_subscription[chat_id].mfd_user.remove(user_id)
            if self.ADD_MFD_THREAD in text:
                thread_id = int(text.split(self.ADD_MFD_THREAD)[1])
                self.users_subscription[chat_id].mfd_thread.append(thread_id)
            if self.REMOVE_MFD_THREAD in text:
                thread_id = int(text.split(self.REMOVE_MFD_THREAD)[1])
                self.users_subscription[chat_id].mfd_thread.remove(thread_id)
        except Exception as e:
            print("Unexpected error:", text, e)

        self.db.save_user_data(self.users_subscription)

        return res

    def check_new(self, chat_id) -> List[str]:
        res: List[str] = []
        if chat_id in self.users_subscription:
            if self.users_subscription[chat_id].alenka:
                res += self.db.update("alenka_news", sources.AlenkaNews().check_update())
                res += self.db.update("alenka_post", sources.AlenkaPost().check_update())
            for user in self.users_subscription[chat_id].mfd_user:
                res += self.db.update("mfd_user_comment", sources.MfdUserCommentSource(user).check_update())
                res += self.db.update("mfd_user_post", sources.MfdUserPostSource(user).check_update())
            for thread in self.users_subscription[chat_id].mfd_thread:
                res += self.db.update("mfd_thread", sources.MfdForumThreadSource(thread).check_update())

        # remove duplicates
        res = list(set(res))
        return res

    def settings(self, chat_id):
        if chat_id in self.users_subscription:
            return self.users_subscription[chat_id]
        else:
            return "Пользователь не найден"

    def check_all(self):
        chat_list = []
        data_list = []
        for user in self.users_subscription:
            chat_list.append(user)
            data_list.append(self.check_new(user))

        return chat_list, data_list
