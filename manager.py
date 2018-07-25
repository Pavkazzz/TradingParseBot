# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from database import DataBase
import sources
import typing


@dataclass
class SingleData:
    id: int = field(default=0)
    name: str = field(default="")


@dataclass
class Data:
    mfd_user: typing.List[SingleData] = field(default_factory=list)
    mfd_thread: typing.List[SingleData] = field(default_factory=list)
    alenka: bool = field(default=False)


class Manager:
    db: DataBase
    ADD_ALENKA = "add_alenka"  # Включить новости с аленки
    REMOVE_ALENKA = "remove_alenka"  # Выключить новости с аленки
    ADD_MFD_USER = "add_mfd_user"  # + id - Добавить mfd пользователя по id
    REMOVE_MFD_USER = "remove_mfd_user"  # + id - Удалить mfd пользователя по id
    ADD_MFD_THREAD = "add_mfd_thread"  # + id - Добавить mfd форум по id
    REMOVE_MFD_THREAD = "remove_mfd_tread"  # + id - Удалить mfd форум по id

    def __init__(self, clear_start=False):
        self.db = DataBase(clear_start)
        self.users_subscription = self.db.load_user_data()

    def start(self, chat_id):
        if chat_id not in self.users_subscription:
            self.users_subscription[chat_id] = Data()

    def new_command(self, chat_id, command, data: SingleData = SingleData()) -> str:
        result: str = "Команда не найдена"
        try:
            # Alenka
            if command == self.ADD_ALENKA:
                self.users_subscription[chat_id].alenka = True
                result = "Теперь вы подписаны на https://alenka.capital"
            if command == self.REMOVE_ALENKA:
                self.users_subscription[chat_id].alenka = False
                result = "Теперь вы отписаны от новостей с https://alenka.capital"

            # Mfd user
            if command == self.ADD_MFD_USER:
                if data not in self.users_subscription[chat_id].mfd_user:
                    self.users_subscription[chat_id].mfd_user.append(data)
                    result = f"Подписка на mfd пользователя {data.name}"
                else:
                    result = f"Вы уже подписаны на пользователя {data.name}"
            if command == self.REMOVE_MFD_USER:
                self.users_subscription[chat_id].mfd_user.remove(data)
                result = f"Отписка от mfd пользователя {data.name}"
            # Mfd thread
            if command == self.ADD_MFD_THREAD:
                if data not in self.users_subscription[chat_id].mfd_thread:
                    self.users_subscription[chat_id].mfd_thread.append(data)
                    result = f"Подписка на mfd тему {data.name}"
                else:
                    result = f"Вы уже подписаны на тему {data.name}"
            if command == self.REMOVE_MFD_THREAD:
                self.users_subscription[chat_id].mfd_thread.remove(data)
                result = f"Отписка от mfd форума {data.name}"
        except KeyError as e:
            print(f"Unexpected key error: {command} {data}, e:{e}")

        self.db.save_user_data(self.users_subscription)

        return result

    def settings(self, chat_id) -> typing.Union[str, Data]:
        if chat_id in self.users_subscription:
            return self.users_subscription[chat_id]
        else:
            return "Пользователь не найден"

    def check_new(self, chat_id) -> List[str]:
        res: List[str] = []
        if chat_id in self.users_subscription:
            if self.users_subscription[chat_id].alenka:
                res += self.db.update(f"alenka_news {chat_id}", sources.AlenkaNews().check_update())
                res += self.db.update(f"alenka_post {chat_id}", sources.AlenkaPost().check_update())
            for user in self.users_subscription[chat_id].mfd_user:
                res += self.db.update(f"mfd_user_comment {chat_id}",
                                      sources.MfdUserCommentSource().add_data(user.id).check_update())
                res += self.db.update(f"mfd_user_post {chat_id}",
                                      sources.MfdUserPostSource().add_data(user.id).check_update())
            for thread in self.users_subscription[chat_id].mfd_thread:
                res += self.db.update(f"mfd_thread {chat_id}",
                                      sources.MfdForumThreadSource().add_data(thread.id).check_update())

        # remove duplicates
        res = list(set(res))
        return res

    def check_all(self):
        for user in self.users_subscription:
            yield user, self.check_new(user)

    def resolve_mfd_thread_link(self, cid, text):
        try:
            tid, name = sources.MfdForumThreadSource().resolve_link(text)
            self.new_command(cid, Manager.ADD_MFD_THREAD, SingleData(tid, name))
            return name
        except Exception as e:
            print(e)
            return None

    def resolve_mfd_user_link(self, cid, text):
        try:
            tid, name = sources.MfdUserPostSource().resolve_link(text)
            self.new_command(cid, Manager.ADD_MFD_USER, SingleData(tid, name))
            return name
        except Exception as e:
            print(e)
            return None

    def find_mfd_thread(self, cid, text):
        title = []
        res = ""
        try:
            title, tid, name = sources.MfdForumThreadSource().find_thread(text)
            if tid is not None and len(title) == 1:
                res = self.new_command(cid, Manager.ADD_MFD_THREAD, SingleData(tid, name))
        except Exception as e:
            print(e)
        finally:
            return title, res

    def find_mfd_user(self, cid, text, rating):
        users = ()
        res = ""
        try:
            users = sources.MfdUserPostSource().find_user(text)
            # Если есть рейтинг, пытаемся найти нашего(Нажали на кнопку)
            if rating > -1:
                users = tuple(filter(lambda x: x[1] == text and x[3] == rating, users))

            if len(users) == 1:
                res = self.new_command(cid, Manager.ADD_MFD_USER, SingleData(users[0][0], users[0][1]))

        except Exception as e:
            print(e)
        finally:
            return users, res
