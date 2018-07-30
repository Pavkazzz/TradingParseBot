import json
import pickle
import typing
from pathlib import Path
import os

from hashlib import blake2s

from sources import Page


class DataBase:
    def __init__(self, clear_start=False):
        self.data_file = "data/database{id}.json"
        self.user_file = "data/users.pkl"
        self.init_database(clear_start)
        for file in os.listdir("data"):
            if file.endswith("json"):
                self.create_db(f"data/{file}")


    def update(self, key, page: Page, chat_id) -> typing.List[str]:
        posts = [md.format() for md in page.posts]
        res = []
        file = Path(self.data_file.format(id=chat_id))
        if not file.is_file():
            self.create_db(file)

        with open(self.data_file.format(id=chat_id), 'r+') as database:
            data = json.load(database)
            database.truncate(0)
            hash_list = []
            for post in posts:
                bhash = blake2s(post.encode('utf-8')).hexdigest()
                hash_list.append(bhash)
                try:
                    if bhash not in data[key]:
                        res.append(post)
                except KeyError:
                    res.append(post)

            data[key] = hash_list
            database.seek(0)
            json.dump(data, database)
        return res

    # Создаем файл бд и приводим в изначальное состояние
    def init_database(self, clear=False):
        if clear:
            self.save_user_data({})

    def create_db(self, file):
        with open(file, 'w+') as database:
            init = {}
            json.dump(init, database)

    def save_user_data(self, users):
        with open(self.user_file, 'wb') as f:
            pickle.dump(users, f)

    def load_user_data(self):
        res = {}
        try:
            with open(self.user_file, 'rb') as f:
                res = pickle.load(f)
        except FileNotFoundError as e:
            self.save_user_data(res)

        return res
