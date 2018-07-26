import typing

from sources import Page
from hashlib import blake2s
import json
import pickle


class DataBase:
    def __init__(self, clear=False):
        self.data_file = "data/database.json"
        self.user_file = "data/users.pkl"
        self.init_database()
        if clear:
            self.create_db()
            self.save_user_data({})

    def update(self, key, page: Page) -> typing.List[str]:
        posts = [md.format() for md in page.posts]
        res = []
        with open(self.data_file, 'r+') as database:
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
    def init_database(self):
        try:
            with open(self.data_file, 'r') as database:
                json.load(database)
        except (json.decoder.JSONDecodeError, FileNotFoundError) as e:
            print(f"Не могу прочитать {self.data_file}, создаю новый")
            self.create_db()

    def create_db(self):
        with open(self.data_file, 'w+') as database:
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
