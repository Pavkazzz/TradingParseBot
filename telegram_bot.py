# -*- coding: utf-8 -*-
import logging
import telegram
from telegram.ext import Updater, CommandHandler
from settings import token, REQUEST_KWARGS
from manager import Manager

manager = Manager()

# Функция старта
def start(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text="Привет это бот для отслеживания блога mfd.ru и alenka.capital")
    manager.start(chat_id)


# функция добавления
def new_command(bot, update):
    chat_id = update.message.chat_id
    text = manager.new_command(chat_id, update.message.text)
    if text:
        bot.send_message(chat_id=chat_id, text=text)


def check_update(bot, job):
    for chat, data in manager.check_all():
        send_data(bot, chat, data)

def check_new(bot, update):
    chat_id = update.message.chat_id
    data = manager.check_new(chat_id)
    send_data(bot, chat_id, data)


def send_data(bot, chat_id, data):
    for msg in data:
        try:
            bot.send_message(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN,
                             disable_web_page_preview=True)
        except Exception as e:
            print(e, msg)


def show_help(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text="Для добавления mfd user -> /add_mfd_user id_user\n"
                                           "Для добавления mfd forum -> /add_mfd_thread id_thread\n"
                                           "Для добавления новостей с аленки -> /add_alenka")


def formation_text(bot, update):
    text = "[Спокойный Скрудж Макдак](http://mfd.ru/forum/poster/?id=88887)"
    bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)


def settings(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=str(manager.settings(chat_id)))


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
updater = Updater(token, request_kwargs=REQUEST_KWARGS)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler(manager.ADD_ALENKA, new_command))
dispatcher.add_handler(CommandHandler(manager.REMOVE_ALENKA, new_command))
dispatcher.add_handler(CommandHandler(manager.ADD_MFD_USER, new_command))
dispatcher.add_handler(CommandHandler(manager.REMOVE_MFD_USER, new_command))
dispatcher.add_handler(CommandHandler(manager.ADD_MFD_THREAD, new_command))
dispatcher.add_handler(CommandHandler(manager.REMOVE_MFD_THREAD, new_command))
dispatcher.add_handler(CommandHandler('help', show_help))
dispatcher.add_handler(CommandHandler('settings', settings))
dispatcher.add_handler(CommandHandler('test', formation_text))
dispatcher.add_handler(CommandHandler('check_new', check_new))
j = updater.job_queue
job_minute = j.run_repeating(check_update, interval=60, first=0)
updater.start_polling()
updater.idle()
