# -*- coding: utf-8 -*-
import asyncio
import logging
import typing
from dataclasses import dataclass, field
from enum import IntEnum, unique
from typing import Tuple, List, Dict

import fast_json
from aiotg import Bot

from trading_bot.database import DataBase
from trading_bot.sources import sources
from trading_bot.telegram_sender import send_message, remove_message

log = logging.getLogger(__name__)


@unique
class State(IntEnum):
    IDLE = 1
    MFD_USER_ADD = 2
    MFD_USER_REMOVE = 3
    MFD_THREAD_ADD = 4
    MFD_THREAD_REMOVE = 5


@dataclass(unsafe_hash=True)
class SingleData:
    id: int = field(default=0)
    name: str = field(default="")


@dataclass
class Data:
    mfd_user: typing.List[SingleData] = field(default_factory=list)
    mfd_thread: typing.List[SingleData] = field(default_factory=list)
    alenka: bool = field(default=False)
    username: str = field(default="")
    state: State = field(default=State.IDLE)

    def remove_duplicate(self):
        self.mfd_user = list(dict.fromkeys(self.mfd_user))
        self.mfd_thread = list(dict.fromkeys(self.mfd_thread))

    def all_tasks(self):
        return self.mfd_thread + self.mfd_user


@fast_json.convert.register(Data)
def serialize(value: Data):
    return {
        "mfd_user": [val.name for val in value.mfd_user],
        "mfd_thread": [val.name for val in value.mfd_thread],
        "alenka": value.alenka,
    }


class Manager:
    ADD_ALENKA = "add_alenka"  # Включить новости с аленки
    REMOVE_ALENKA = "remove_alenka"  # Выключить новости с аленки
    ADD_MFD_USER = "add_mfd_user"  # + id - Добавить mfd пользователя по id
    REMOVE_MFD_USER = "remove_mfd_user"  # + id - Удалить mfd пользователя по id
    ADD_MFD_THREAD = "add_mfd_thread"  # + id - Добавить mfd форум по id
    REMOVE_MFD_THREAD = "remove_mfd_tread"  # + id - Удалить mfd форум по id

    def __init__(self, clear_start=False, redis=None):
        self.current_data = {}

        self.db: DataBase = DataBase(clear_start)
        self.users_subscription: Dict[int, Data] = self.db.load_user_data()
        self.sended_msg = self.db.load_user_messages()

        for user_id in self.users_subscription:
            if user_id not in self.sended_msg:
                self.sended_msg[user_id] = {}

        self.sources = {
            "alenka_post": sources.AlenkaPost(redis=redis),
            "alenka_news": sources.AlenkaNews(redis=redis),
            "mfd_user_post": sources.MfdUserPostSource(),
            "mfd_user_comment": sources.MfdUserCommentSource(),
            "mfd_thread": sources.MfdForumThreadSource(),
        }

    async def send_to_all_users(self, bot, text: str):
        for chat_id in self.users_subscription.keys():
            await send_message(self, bot, chat_id, 0, text, 0)

    async def remove_message(self, bot, message_id):
        for chat_id in self.users_subscription.keys():
            await remove_message(
                bot, chat_id, self.get_sended_id(chat_id, message_id)
            )

    async def manage_subscription_user(self, user_name, value):
        for user in self.users_subscription.values():
            if user_name == user:
                user.alenka_confirmed = value

    def recreate_users(self, bot: Bot):
        for user in self.db.user_list():
            if user not in self.users_subscription:
                self.users_subscription[user] = Data()
                try:
                    bot.send_message(
                        user,
                        "По причине переноса на бота на новые мощности,"
                        " возникли проблемы с востановлением подписок. "
                        "Приношу извинения за доставленные неудобства.",
                    )
                except Exception:
                    log.exception("Error recreate user: %r", user)

        self.db.save_user_data(self.users_subscription)

    def start(self, chat_id, username):
        if chat_id not in self.users_subscription:
            self.users_subscription[chat_id] = Data(username=username)
            self.sended_msg[chat_id] = {}

    def stop(self, chat_id):
        if chat_id in self.users_subscription:
            del self.users_subscription[chat_id]
            del self.sended_msg[chat_id]

    async def new_command(
        self, chat_id, command, data=SingleData()
    ) -> Tuple[str, List[sources.SinglePost]]:
        result: str = "Команда не найдена"
        current_data = []
        try:
            current_data, result = await self.new_alenka(
                chat_id, command, current_data, result
            )

            current_data, result = await self.new_mfd_user(
                chat_id, command, current_data, data, result
            )
            # Mfd thread
            current_data, result = await self.new_mfd_thread(
                chat_id, command, current_data, data, result
            )
        except KeyError:
            log.exception("Unexpected key error: %r, %r", command, data)

        self.db.save_user_data(self.users_subscription)
        return result, current_data

    async def new_mfd_thread(
        self, chat_id, command, current_data, data, result
    ):
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
        return current_data, result

    async def new_mfd_user(self, chat_id, command, current_data, data, result):
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
        return current_data, result

    async def new_alenka(self, chat_id, command, current_data, result):
        # Alenka
        if command == self.ADD_ALENKA:
            self.users_subscription[chat_id].alenka = True
            current_data = await self.check_new_alenka(chat_id)
            result = "Теперь вы подписаны на https://alenka.capital"
        if command == self.REMOVE_ALENKA:
            self.users_subscription[chat_id].alenka = False
            result = "Теперь вы отписаны от новостей с https://alenka.capital"
        return current_data, result

    def settings(self, chat_id) -> typing.Union[str, Data]:
        if chat_id not in self.users_subscription:
            self.start(chat_id, "tests")
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
            self.current_data["alenka_news"] = await self.sources[
                "alenka_news"
            ].check_update()

        if "alenka_post" not in self.current_data:
            self.current_data["alenka_post"] = await self.sources[
                "alenka_post"
            ].check_update()

        res = []
        res += self.db.update(
            f"alenka_news", self.current_data["alenka_news"], chat_id
        )
        res += self.db.update(
            f"alenka_post", self.current_data["alenka_post"], chat_id
        )
        return res

    async def check_mfd_user(self, user, chat_id):

        if f"mfd_user_comment {user.id}" not in self.current_data:
            await self.update_mfd_user_comment(user.id)

        if f"mfd_user_post {user.id}" not in self.current_data:
            await self.update_mfd_user_post(user.id)

        res = []
        res += self.db.update(
            f"mfd_user_comment {user.id} {chat_id}",
            self.current_data[f"mfd_user_comment {user.id}"],
            chat_id,
        )
        res += self.db.update(
            f"mfd_user_post {user.id} {chat_id}",
            self.current_data[f"mfd_user_post {user.id}"],
            chat_id,
        )
        return res

    async def check_mfd_thread(self, thread, chat_id):

        if f"mfd_thread {thread.id}" not in self.current_data:
            await self.update_mfd_thread(thread.id)

        return self.db.update(
            f"mfd_thread {thread.id} {chat_id}",
            self.current_data[f"mfd_thread {thread.id}"],
            chat_id,
        )

    async def check_new_all(self, save=True) -> typing.AsyncIterable:
        await self.prepare_cache()

        for user in list(self.users_subscription):
            posts = await self.check_new(user)
            message_id = [self.get_sended_id(user, post) for post in posts]
            yield user, list(zip(posts, message_id))

        if save:
            self.save_user_messages()

    async def prepare_cache(self):
        await self.update_alenka()
        await self.update_mfd()

    async def update_alenka(self):
        self.current_data["alenka_news"] = await self.sources[
            "alenka_news"
        ].check_update()
        self.current_data["alenka_post"] = await self.sources[
            "alenka_post"
        ].check_update()

    async def update_mfd(self):
        data_list = Data()
        for user, data in self.users_subscription.items():
            for thread in data.mfd_thread:
                data_list.mfd_thread.append(thread)
            for mfd_user in data.mfd_user:
                data_list.mfd_user.append(mfd_user)
        data_list.remove_duplicate()

        tasks = [
            self.update_mfd_thread(data.id) for data in data_list.mfd_thread
        ]
        tasks += [
            self.update_mfd_user_post(data.id) for data in data_list.mfd_user
        ]
        tasks += [
            self.update_mfd_user_comment(data.id) for data in data_list.mfd_user
        ]
        await asyncio.gather(*tasks)

    async def update_mfd_user_comment(self, data_id):
        self.current_data[f"mfd_user_comment {data_id}"] = await self.sources[
            "mfd_user_comment"
        ].check_update(data_id)

    async def update_mfd_user_post(self, data_id):
        self.current_data[f"mfd_user_post {data_id}"] = await self.sources[
            "mfd_user_post"
        ].check_update(data_id)

    async def update_mfd_thread(self, data_id):
        self.current_data[f"mfd_thread {data_id}"] = await self.sources[
            "mfd_thread"
        ].check_update(data_id)

    async def resolve_mfd_thread_link(self, cid, text):
        try:
            tid, name = await self.sources["mfd_thread"].resolve_link(text)
            await self.new_command(
                cid, Manager.ADD_MFD_THREAD, SingleData(tid, name)
            )
            return name
        except Exception:
            log.exception("Exception while resolve mfd thread: %r", text)
            return None

    async def resolve_mfd_user_link(self, cid, text):
        try:
            tid, name = await self.sources["mfd_user_post"].resolve_link(text)
            await self.new_command(
                cid, Manager.ADD_MFD_USER, SingleData(tid, name)
            )
            return name
        except Exception:
            log.exception("Exception while resolve user link: %r", text)
            return None

    async def find_mfd_thread(self, cid, text):
        title = []
        res = ""
        try:
            title, tid, name = await self.sources["mfd_thread"].find_thread(
                text
            )
            if tid is not None and len(title) == 1:
                res, _ = await self.new_command(
                    cid, Manager.ADD_MFD_THREAD, SingleData(tid, name)
                )
        except Exception:
            log.exception("Exception while find thread: %r", text)
        finally:
            return title, res

    async def find_mfd_user(self, cid, text, rating):
        users = ()
        res = ""
        try:
            users = await self.sources["mfd_user_post"].find_user(text)
            # Если есть рейтинг, пытаемся найти нашего(Нажали на кнопку)
            if rating > -1:
                users = tuple(
                    filter(lambda x: x[1] == text and x[3] == rating, users)
                )

            if len(users) == 1:
                res, _ = await self.new_command(
                    cid,
                    Manager.ADD_MFD_USER,
                    SingleData(users[0][0], users[0][1]),
                )

        except Exception:
            log.exception(
                "Exception while find user text: %r, rating %r", text, rating
            )
        finally:
            return users, res

    async def config_sources(self, source, url, text):
        self.sources[source].update_cache(url, text)
        await self.update_alenka()

    def get_sended_id(self, chat_id, post):
        try:
            return self.sended_msg[chat_id][post.id]
        except KeyError:
            return 0

    def set_sended_id(self, message_id, chat_id, post_id):
        self.sended_msg[chat_id][post_id] = message_id

    def save_user_messages(self):
        self._remove_old_cache()
        self.db.save_user_messages(self.sended_msg)

    def _remove_old_cache(self):
        """
        Remove message_id from cache which cannot be accuse now
        :return:
        """
        actual_id_list = [
            post.id
            for item in self.current_data.values()
            for post in item.posts
        ]

        for user in self.sended_msg:
            user_msg = frozenset(self.sended_msg[user].keys())
            actual_set = user_msg - frozenset(actual_id_list)
            for i in list(actual_set):
                self.sended_msg[user].pop(i, None)

    def set_username(self, chat_id, username):
        self.users_subscription[chat_id].username = username

    def set_state(self, chat_id, state):
        self.users_subscription[chat_id].state = state

    def state(self, chat_id):
        return self.users_subscription[chat_id].state
