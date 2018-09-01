# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Tuple, List, Union, Set, Any, Dict
from telegram import Bot

from database import DataBase
import sources
import typing


@dataclass(unsafe_hash=True)
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
        self.sended_msg = {}
        self.sources = {}
        self.current_data = {}

        self.db = DataBase(clear_start)
        self.users_subscription: Dict[Data] = self.db.load_user_data()
        for user in self.users_subscription:
            self.sended_msg[user] = {}

        self.sources["alenka_post"] = sources.AlenkaPost()
        self.sources["alenka_news"] = sources.AlenkaNews()
        self.sources["mfd_user_post"] = sources.MfdUserPostSource()
        self.sources["mfd_user_comment"] = sources.MfdUserCommentSource()
        self.sources["mfd_thread"] = sources.MfdForumThreadSource()

    def recreate_users(self, bot: Bot):
        for user in self.db.user_list():
            if user not in self.users_subscription:
                self.users_subscription[user] = Data()
                try:
                    bot.send_message(user, text="По причине переноса на бота на новые мощности, возникли проблемы с "
                                                "востановлением подписок. Приношу извинения за доставленные неудобства.")
                except Exception as e:
                    print(e, user)

        self.db.save_user_data(self.users_subscription, {})

    def start(self, chat_id):
        if chat_id not in self.users_subscription:
            self.users_subscription[chat_id] = Data()
            self.sended_msg[chat_id] = {}

    def stop(self, chat_id):
        if chat_id in self.users_subscription:
            del self.users_subscription[chat_id]

    def new_command(self, chat_id, command, data: SingleData = SingleData()) -> Tuple[str, List[sources.SinglePost]]:
        result: str = "Команда не найдена"
        current_data = []
        try:
            # Alenka
            if command == self.ADD_ALENKA:
                self.users_subscription[chat_id].alenka = True
                current_data = self.check_new_alenka(chat_id)
                result = "Теперь вы подписаны на https://alenka.capital"
            if command == self.REMOVE_ALENKA:
                self.users_subscription[chat_id].alenka = False
                result = "Теперь вы отписаны от новостей с https://alenka.capital"

            # Mfd user
            if command == self.ADD_MFD_USER:
                if data not in self.users_subscription[chat_id].mfd_user:
                    self.users_subscription[chat_id].mfd_user.append(data)
                    current_data = self.check_mfd_user(data, chat_id)
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
                    current_data = self.check_mfd_thread(data, chat_id)
                    result = f"Подписка на mfd тему {data.name}"
                else:
                    result = f"Вы уже подписаны на тему {data.name}"
            if command == self.REMOVE_MFD_THREAD:
                self.users_subscription[chat_id].mfd_thread.remove(data)
                result = f"Отписка от mfd форума {data.name}"
        except KeyError as e:
            print(f"Unexpected key error: {command} {data}, e:{e}")

        self.db.save_user_data(self.users_subscription, self.sended_msg)
        return result, current_data

    def settings(self, chat_id) -> typing.Union[str, Data]:
        if chat_id not in self.users_subscription:
            self.start(chat_id)
        return self.users_subscription[chat_id]

    def check_new(self, chat_id) -> List[sources.SinglePost]:
        res = []
        if chat_id in self.users_subscription:
            if self.users_subscription[chat_id].alenka:
                res += self.check_new_alenka(chat_id)
            for user in self.users_subscription[chat_id].mfd_user:
                res += self.check_mfd_user(user, chat_id)
            for thread in self.users_subscription[chat_id].mfd_thread:
                res += self.check_mfd_thread(thread, chat_id)

        return res

    def check_new_alenka(self, chat_id):
        if "alenka_news" not in self.current_data:
            self.current_data["alenka_news"] = self.sources["alenka_news"].check_update()

        if "alenka_post" not in self.current_data:
            self.current_data["alenka_post"] = self.sources["alenka_post"].check_update()

        res = []
        res += self.db.update(f"alenka_news", self.current_data["alenka_news"], chat_id)
        res += self.db.update(f"alenka_post", self.current_data["alenka_post"], chat_id)
        return res

    def check_mfd_user(self, user, chat_id):

        if f"mfd_user_comment {user.id}" not in self.current_data:
            self.current_data[f"mfd_user_comment {user.id}"] = self.sources["mfd_user_comment"].check_update(user.id)

        if f"mfd_user_post {user.id}" not in self.current_data:
            self.current_data[f"mfd_user_post {user.id}"] = self.sources["mfd_user_post"].check_update(user.id)

        res = []
        res += self.db.update(f"mfd_user_comment {user.id} {chat_id}",
                              self.current_data[f"mfd_user_comment {user.id}"], chat_id)
        res += self.db.update(f"mfd_user_post {user.id} {chat_id}",
                              self.current_data[f"mfd_user_post {user.id}"], chat_id)
        return res

    def check_mfd_thread(self, thread, chat_id):

        if f"mfd_thread {thread.id}" not in self.current_data:
            self.current_data[f"mfd_thread {thread.id}"] = self.sources["mfd_thread"].check_update(thread.id)

        return self.db.update(f"mfd_thread {thread.id} {chat_id}",
                              self.current_data[f"mfd_thread {thread.id}"], chat_id)

    def check_new_all(self) -> Tuple[int, List[Tuple[sources.SinglePost, int]]]:
        self.update_all_sources()
        self.db.save_user_messages(self.sended_msg)

        for user in list(self.users_subscription):
            posts = self.check_new(user)
            message_id = []
            for post in posts:
                if post.id not in self.sended_msg[user]:
                    message_id.append(0)
                else:
                    message_id.append(self.sended_msg[user][post.id])
            yield user, list(zip(posts, message_id))

    def update_all_sources(self):
        self.update_alenka()
        self.update_mfd()

    def update_alenka(self):
        self.current_data["alenka_news"] = self.sources["alenka_news"].check_update()
        self.current_data["alenka_post"] = self.sources["alenka_post"].check_update()

    def update_mfd(self):
        data_list = Data()
        for user, data in self.users_subscription.items():
            for thread in data.mfd_thread:
                data_list.mfd_thread.append(thread)
            for mfd_user in data.mfd_user:
                data_list.mfd_user.append(mfd_user)

        for data in data_list.mfd_thread:
            self.current_data[f"mfd_thread {data.id}"] = self.sources["mfd_thread"].check_update(data)

        for data in data_list.mfd_user:
            self.current_data[f"mfd_user_post {data.id}"] = self.sources["mfd_user_post"].check_update(data)
            self.current_data[f"mfd_user_comment {data.id}"] = self.sources["mfd_user_comment"].check_update(data)

    def resolve_mfd_thread_link(self, cid, text):
        try:
            tid, name = self.sources["mfd_thread"].resolve_link(text)
            self.new_command(cid, Manager.ADD_MFD_THREAD, SingleData(tid, name))
            return name
        except Exception as e:
            print(e)
            return None

    def resolve_mfd_user_link(self, cid, text):
        try:
            tid, name = self.sources["mfd_user_post"].resolve_link(text)
            self.new_command(cid, Manager.ADD_MFD_USER, SingleData(tid, name))
            return name
        except Exception as e:
            print(e)
            return None

    def find_mfd_thread(self, cid, text):
        title = []
        res = ""
        try:
            title, tid, name = self.sources["mfd_thread"].find_thread(text)
            if tid is not None and len(title) == 1:
                res, _ = self.new_command(cid, Manager.ADD_MFD_THREAD, SingleData(tid, name))
        except Exception as e:
            print(e)
        finally:
            return title, res

    def find_mfd_user(self, cid, text, rating):
        users = ()
        res = ""
        try:
            users = self.sources["mfd_user_post"].find_user(text)
            # Если есть рейтинг, пытаемся найти нашего(Нажали на кнопку)
            if rating > -1:
                users = tuple(filter(lambda x: x[1] == text and x[3] == rating, users))

            if len(users) == 1:
                res, _ = self.new_command(cid, Manager.ADD_MFD_USER, SingleData(users[0][0], users[0][1]))

        except Exception as e:
            print(e)
        finally:
            return users, res

    def config_sources(self, source, generator=None):
        self.sources[source].set_generator(generator)
        self.update_alenka()

    def set_message_id(self, message_id, chat_id, post_id):
        self.sended_msg[chat_id][post_id] = message_id
