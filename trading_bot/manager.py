# -*- coding: utf-8 -*-
import asyncio
import logging
import typing
from dataclasses import dataclass, field
from typing import Tuple, List, Dict

from aiotg import Bot

from trading_bot import sources
from trading_bot.database import DataBase


@dataclass(unsafe_hash=True)
class SingleData:
    id: int = field(default=0)
    name: str = field(default="")


@dataclass
class Data:
    mfd_user: typing.List[SingleData] = field(default_factory=list)
    mfd_thread: typing.List[SingleData] = field(default_factory=list)
    alenka: bool = field(default=False)

    def remove_duplicate(self):
        self.mfd_user = list(dict.fromkeys(self.mfd_user))
        self.mfd_thread = list(dict.fromkeys(self.mfd_thread))

    def all_tasks(self):
        return self.mfd_thread + self.mfd_user


class Manager:
    ADD_ALENKA = "add_alenka"  # Включить новости с аленки
    REMOVE_ALENKA = "remove_alenka"  # Выключить новости с аленки
    ADD_MFD_USER = "add_mfd_user"  # + id - Добавить mfd пользователя по id
    REMOVE_MFD_USER = "remove_mfd_user"  # + id - Удалить mfd пользователя по id
    ADD_MFD_THREAD = "add_mfd_thread"  # + id - Добавить mfd форум по id
    REMOVE_MFD_THREAD = "remove_mfd_tread"  # + id - Удалить mfd форум по id

    def __init__(self, clear_start=False):
        self.current_data = {}

        self.db: DataBase = DataBase(clear_start)
        self.users_subscription: Dict[Data] = self.db.load_user_data()
        self.sended_msg = self.db.load_user_messages()

        for user_id in self.users_subscription:
            if user_id not in self.sended_msg:
                self.sended_msg[user_id] = {}

        self.sources = {
            "alenka_post": sources.AlenkaPost(),
            "alenka_news": sources.AlenkaNews(),
            "mfd_user_post": sources.MfdUserPostSource(),
            "mfd_user_comment": sources.MfdUserCommentSource(),
            "mfd_thread": sources.MfdForumThreadSource()
        }

    def recreate_users(self, bot: Bot):
        for user in self.db.user_list():
            if user not in self.users_subscription:
                self.users_subscription[user] = Data()
                try:
                    bot.send_message(user, "По причине переноса на бота на новые мощности,"
                                           " возникли проблемы с востановлением подписок. "
                                           "Приношу извинения за доставленные неудобства.")
                except Exception:
                    logging.exception('Error recreate user: %r', user)

        self.db.save_user_data(self.users_subscription)

    def start(self, chat_id):
        if chat_id not in self.users_subscription:
            self.users_subscription[chat_id] = Data()
            self.sended_msg[chat_id] = {}

    def stop(self, chat_id):
        if chat_id in self.users_subscription:
            del self.users_subscription[chat_id]
            del self.sended_msg[chat_id]

    async def new_command(self, chat_id, command, data: SingleData = SingleData()) -> Tuple[
        str, List[sources.SinglePost]]:
        result: str = "Команда не найдена"
        current_data = []
        try:
            # Alenka
            if command == self.ADD_ALENKA:
                self.users_subscription[chat_id].alenka = True
                current_data = await self.check_new_alenka(chat_id)
                result = "Теперь вы подписаны на https://alenka.capital"
            if command == self.REMOVE_ALENKA:
                self.users_subscription[chat_id].alenka = False
                result = "Теперь вы отписаны от новостей с https://alenka.capital"

            # Mfd user
            if command == self.ADD_MFD_USER:
                if data not in self.users_subscription[chat_id].mfd_user:
                    self.users_subscription[chat_id].mfd_user.append(data)
                    current_data = await self.check_mfd_user(data, chat_id)
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
                    current_data = await self.check_mfd_thread(data, chat_id)
                    result = f"Подписка на mfd тему {data.name}"
                else:
                    result = f"Вы уже подписаны на тему {data.name}"
            if command == self.REMOVE_MFD_THREAD:
                self.users_subscription[chat_id].mfd_thread.remove(data)
                result = f"Отписка от mfd форума {data.name}"
        except KeyError as e:
            print(f"Unexpected key error: {command} {data}, e:{e}")

        self.db.save_user_data(self.users_subscription)
        return result, current_data

    def settings(self, chat_id) -> typing.Union[str, Data]:
        if chat_id not in self.users_subscription:
            self.start(chat_id)
        return self.users_subscription[chat_id]

    async def check_new(self, chat_id) -> List[sources.SinglePost]:
        res = []
        if chat_id in self.users_subscription:
            if self.users_subscription[chat_id].alenka:
                res += await self.check_new_alenka(chat_id)
            for user in self.users_subscription[chat_id].mfd_user:
                res += await self.check_mfd_user(user, chat_id)
            for thread in self.users_subscription[chat_id].mfd_thread:
                res += await self.check_mfd_thread(thread, chat_id)

        res = list(dict.fromkeys(res))

        return res

    async def check_new_alenka(self, chat_id):
        if "alenka_news" not in self.current_data:
            self.current_data["alenka_news"] = await self.sources["alenka_news"].check_update()

        if "alenka_post" not in self.current_data:
            self.current_data["alenka_post"] = await self.sources["alenka_post"].check_update()

        res = []
        res += self.db.update(f"alenka_news", self.current_data["alenka_news"], chat_id)
        res += self.db.update(f"alenka_post", self.current_data["alenka_post"], chat_id)
        return res

    async def check_mfd_user(self, user, chat_id):

        if f"mfd_user_comment {user.id}" not in self.current_data:
            await self.update_mfd_user_comment(user)

        if f"mfd_user_post {user.id}" not in self.current_data:
            await self.update_mfd_user_post(user)

        res = []
        res += self.db.update(f"mfd_user_comment {user.id} {chat_id}",
                              self.current_data[f"mfd_user_comment {user.id}"], chat_id)
        res += self.db.update(f"mfd_user_post {user.id} {chat_id}",
                              self.current_data[f"mfd_user_post {user.id}"], chat_id)
        return res

    async def check_mfd_thread(self, thread, chat_id):

        if f"mfd_thread {thread.id}" not in self.current_data:
            await self.update_mfd_thread(thread)

        return self.db.update(f"mfd_thread {thread.id} {chat_id}",
                              self.current_data[f"mfd_thread {thread.id}"], chat_id)

    async def check_new_all(self) -> typing.AsyncIterable:
        await self.prepare_cache()

        for user in list(self.users_subscription):
            posts = await self.check_new(user)
            message_id = []
            for post in posts:
                if post.id not in self.sended_msg[user]:
                    message_id.append(0)
                else:
                    message_id.append(self.sended_msg[user][post.id])
            yield user, list(zip(posts, message_id))
        self.save_user_messages()

    async def prepare_cache(self):
        tasks = [self.update_alenka(), self.update_mfd()]
        await asyncio.gather(*tasks)

    async def update_alenka(self):
        self.current_data["alenka_news"] = await self.sources["alenka_news"].check_update()
        self.current_data["alenka_post"] = await self.sources["alenka_post"].check_update()

    async def update_mfd(self):
        data_list = Data()
        for user, data in self.users_subscription.items():
            for thread in data.mfd_thread:
                data_list.mfd_thread.append(thread)
            for mfd_user in data.mfd_user:
                data_list.mfd_user.append(mfd_user)
        data_list.remove_duplicate()

        tasks = [self.update_mfd_thread(data) for data in data_list.mfd_thread]
        tasks += [self.update_mfd_user_post(data) for data in data_list.mfd_user]
        tasks += [self.update_mfd_user_comment(data) for data in data_list.mfd_thread]
        await asyncio.gather(*tasks)

    async def update_mfd_user_comment(self, data):
        self.current_data[f"mfd_user_comment {data.id}"] = await self.sources["mfd_user_comment"].check_update()

    async def update_mfd_user_post(self, data):
        self.current_data[f"mfd_user_post {data.id}"] = await self.sources["mfd_user_post"].check_update()

    async def update_mfd_thread(self, data):
        self.current_data[f"mfd_thread {data.id}"] = await self.sources["mfd_thread"].check_update()

    async def resolve_mfd_thread_link(self, cid, text):
        try:
            tid, name = await self.sources["mfd_thread"].resolve_link(text)
            await self.new_command(cid, Manager.ADD_MFD_THREAD, SingleData(tid, name))
            return name
        except Exception:
            logging.exception('Exception while resolve mfd thread: %r', text)
            return None

    async def resolve_mfd_user_link(self, cid, text):
        try:
            tid, name = await self.sources["mfd_user_post"].resolve_link(text)
            await self.new_command(cid, Manager.ADD_MFD_USER, SingleData(tid, name))
            return name
        except Exception:
            logging.exception('Exception while resolve user link: %r', text)
            return None

    async def find_mfd_thread(self, cid, text):
        title = []
        res = ""
        try:
            title, tid, name = await self.sources["mfd_thread"].find_thread(text)
            if tid is not None and len(title) == 1:
                res, _ = await self.new_command(cid, Manager.ADD_MFD_THREAD, SingleData(tid, name))
        except Exception:
            logging.exception('Exception while find thread: %r', text)
        finally:
            return title, res

    async def find_mfd_user(self, cid, text, rating):
        users = ()
        res = ""
        try:
            users = await self.sources["mfd_user_post"].find_user(text)
            # Если есть рейтинг, пытаемся найти нашего(Нажали на кнопку)
            if rating > -1:
                users = tuple(filter(lambda x: x[1] == text and x[3] == rating, users))

            if len(users) == 1:
                res, _ = await self.new_command(cid, Manager.ADD_MFD_USER, SingleData(users[0][0], users[0][1]))

        except Exception:
            logging.exception('Exception while find user text: %r, rating %r', text, rating)
        finally:
            return users, res

    async def config_sources(self, source, text):
        self.sources[source].update_cache(text)
        await self.update_alenka()

    def set_message_id(self, message_id, chat_id, post_id):
        self.sended_msg[chat_id][post_id] = message_id

    def save_user_messages(self):
        self._remove_old_cache()
        self.db.save_user_messages(self.sended_msg)

    def _remove_old_cache(self):
        """
        Remove message_id from cache which cannot be accuse now
        :return:
        """
        actual_id_list = [post.id for item in self.current_data.values() for post in item.posts]

        for user in self.sended_msg:
            user_msg = frozenset(self.sended_msg[user].keys())
            actual_set = user_msg - frozenset(actual_id_list)
            for i in list(actual_set):
                self.sended_msg[user].pop(i, None)
