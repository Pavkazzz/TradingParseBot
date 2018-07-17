# -*- coding: utf-8 -*-
import logging
from telegram.ext import Updater, CommandHandler
from settings import token


# Функция старта
def start(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text="Привет это бот для отслеживания блога mfd.ru")


# функция добавления
def add_new(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text="Кого желаете добавить?")


def check_new():
    pass


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
updater = Updater(token)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('add', add_new))
j = updater.job_queue
job_minute = j.run_repeating(check_new, interval=60, first=0)
updater.start_polling()
updater.idle()
