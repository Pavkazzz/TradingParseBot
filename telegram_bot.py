# -*- coding: utf-8 -*-
import logging
import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import Updater, CommandHandler, RegexHandler, Filters, MessageHandler
from settings import token, REQUEST_KWARGS
from manager import Manager
from sources import SmartLab

manager = Manager()
for posts in manager.check_new_all():
    # print(posts)
    pass

IDLE, MFD_USER_ADD, MFD_USER_REMOVE, MFD_THREAD_ADD, MFD_THREAD_REMOVE = range(5)
state = IDLE


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


# Функция старта
def start(bot, update):
    chat_id = update.message.chat_id
    # bot.send_message(chat_id=chat_id, text="Привет это бот для отслеживания блога mfd.ru и alenka.capital")
    manager.start(chat_id)
    key(bot, update)


def check_update(bot, job):
    for chat, data in manager.check_new_all():
        send_data(bot, chat, data)


def send_data(bot, chat_id, data):
    for msg in data:
        try:
            bot.send_message(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN,
                             disable_web_page_preview=True)
        except Exception as e:
            print(e, msg)


def print_settings(bot: Bot, update):
    chat_id = update.message.chat_id
    current_settings = manager.settings(chat_id)
    msg = ""

    if current_settings.alenka or len(current_settings.mfd_user) > 0 or len(current_settings.mfd_thread) > 0:
        msg += "Вы подписаны на:\n"
    else:
        msg = "У вас нет активных подписок."
        bot.send_message(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)
        return

    if current_settings.alenka:
        msg += "  Новости с [https://alenka.capital](alenka.capital)"

    msg += "\n\n"

    if len(current_settings.mfd_user) == 1:
        for user in current_settings.mfd_user:
            msg += f"  Пользователя [{user.name}](http://forum.mfd.ru/forum/poster/?id={user.id})\n"
    if len(current_settings.mfd_user) > 1:
        msg += "  На пользователей: \n"
        for user in current_settings.mfd_user:
            msg += f"    [{user.name}](http://forum.mfd.ru/forum/poster/?id={user.id})\n"

    msg += "\n"

    if len(current_settings.mfd_thread) == 1:
        for thread in current_settings.mfd_thread:
            msg += f"  Тему [{thread.name}](http://forum.mfd.ru/forum/thread/?id={thread.id})\n"
    if len(current_settings.mfd_thread) > 1:
        msg += f"  На темы: \n"
        for thread in current_settings.mfd_thread:
            msg += f"    [{thread.name}](http://forum.mfd.ru/forum/thread/?id={thread.id})\n"

    bot.send_message(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.ERROR)
logger = logging.getLogger(__name__)
updater = Updater(token, request_kwargs=REQUEST_KWARGS)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))


# dispatcher.add_handler(CommandHandler('test', formation_text))

# Начальная настройка клавиатуры
def key(bot, update):
    global state
    state = IDLE

    options = ["Подписки", "About"]
    reply_markup = ReplyKeyboardMarkup(build_menu(options, n_cols=2, header_buttons=["Смартлаб топ 24 часа"]))
    bot.send_message(chat_id=update.message.chat_id, text="Привет", reply_markup=reply_markup)


def keyboard_markup(options=None, header=None, n_col=2):
    if options is None:
        return ReplyKeyboardRemove()
    else:
        return ReplyKeyboardMarkup(build_menu(options, n_cols=n_col, footer_buttons=["Отмена"], header_buttons=header))


def smartlab(bot: Bot, update):
    cid = update.message.chat_id
    sl = SmartLab()

    bot.send_message(cid, sl.check_update().posts[0].format(), parse_mode=telegram.ParseMode.MARKDOWN,
                     disable_web_page_preview=True)


def about(bot: Bot, update):
    cid = update.message.chat_id
    bot.send_message(cid, "Привет. Я бот для оповещения. Не обижайте меня, я буду верно вам служить. \n"
                          "Умею подписываться на пользователей и темы на форуме mfd.ru и оповещать о новых сообщениях\n"
                          "Могу сообщить, когда появляется новая тема или новость на Алёнке. \n"
                          "Пользуйтесь на здоровье!")


def settings(bot, update):
    user = manager.settings(update.message.chat_id)

    if user.alenka:
        alenka = "Отписаться от ALЁNKA"
    else:
        alenka = "Подписаться на ALЁNKA"

    options = [alenka, "MFD.ru тема", "MFD.ru пользователи"]

    bot.send_message(update.message.chat_id, 'Подписки: ',
                     reply_markup=keyboard_markup(options, ["Текущие подписки"], 3))


def subscribe_alenka(bot, update):
    cid = update.message.chat_id
    text, _ = manager.new_command(cid, Manager.ADD_ALENKA)
    bot.send_message(cid, text)
    settings(bot, update)


def unsubscribe_alenka(bot, update):
    cid = update.message.chat_id
    text, _ = manager.new_command(cid, Manager.REMOVE_ALENKA)
    bot.send_message(cid, text)
    settings(bot, update)


def mfd_forum(bot, update):
    cid = update.message.chat_id
    options = ["Добавить mfd тему", "Удалить mfd тему"]
    bot.send_message(cid, "Выберете действие: ", reply_markup=keyboard_markup(options))


def mfd_user(bot, update):
    cid = update.message.chat_id
    options = ["Добавить mfd пользователя", "Удалить mfd пользователя"]
    bot.send_message(cid, "Выберете действие: ", reply_markup=keyboard_markup(options))


def mfd_user_add(bot, update):
    cid = update.message.chat_id
    bot.send_message(cid, "Введите имя темы или ссылку на пользователя.\nЕсли передумали, введите \"Отмена\" ",
                     reply_markup=keyboard_markup())
    global state
    state = MFD_USER_ADD


def mfd_user_remove(bot, update):
    cid = update.message.chat_id
    bot.send_message(cid, "Выберете пользователя для удаления: ",
                     reply_markup=keyboard_markup([data.name for data in manager.settings(cid).mfd_user], n_col=1))
    global state
    state = MFD_USER_REMOVE


def mfd_forum_add(bot, update):
    cid = update.message.chat_id
    bot.send_message(cid, "Введите имя темы или ссылку на тему или любое сообщение этой темы ",
                     reply_markup=keyboard_markup())
    global state
    state = MFD_THREAD_ADD


def mfd_forum_remove(bot, update):
    cid = update.message.chat_id
    bot.send_message(cid, "Выберете тему для удаления: ",
                     reply_markup=keyboard_markup([data.name for data in manager.settings(cid).mfd_thread], n_col=1))
    global state
    state = MFD_THREAD_REMOVE


def received_information(bot, update):
    if state == IDLE:
        return
    if state == MFD_THREAD_ADD:
        mfd_add_thread(bot, update)
    if state == MFD_THREAD_REMOVE:
        mfd_remove_thread(bot, update)
    if state == MFD_USER_ADD:
        mfd_add_user(bot, update)
    if state == MFD_USER_REMOVE:
        mfd_remove_user(bot, update)


def mfd_remove_user(bot: Bot, update):
    text = str(update.message.text)
    cid = update.message.chat_id
    res = ""
    for data in manager.settings(cid).mfd_user:
        if data.name == text:
            res, _ = manager.new_command(cid, Manager.REMOVE_MFD_USER, data)
    if res:
        bot.send_message(cid, res)
        settings(bot, update)
    else:
        bot.send_message(cid, "Данный пользователь не найден для удаления. Попробуйте еще раз")


def mfd_remove_thread(bot: Bot, update):
    text = str(update.message.text)
    cid = update.message.chat_id
    res = ""
    for data in manager.settings(cid).mfd_thread:
        if data.name == text:
            res, _ = manager.new_command(cid, Manager.REMOVE_MFD_THREAD, data)

    if res:
        bot.send_message(cid, res)
        settings(bot, update)
    else:
        bot.send_message(cid, "Данная тема не найдена для удаления. Попробуйте еще раз")


def mfd_add_user(bot: Bot, update):
    text = str(update.message.text)
    rating = -1
    if ':' in text:
        try:
            spl = text.split(':')
            text = str(spl[0]).strip()
            rating = int(spl[1])
        except Exception as e:
            print(e)

    cid = update.message.chat_id
    if text.startswith('http'):
        answer = manager.resolve_mfd_user_link(cid, text)
        if answer is not None:
            bot.send_message(cid, f"Пользователь {answer} добавлен в подписки")
            settings(bot, update)
        else:
            bot.send_message(cid, "Пользователь не найден. Проверьте ссылку и попробуйте еще раз")
    else:
        bot.send_chat_action(chat_id=cid, action=telegram.ChatAction.TYPING)
        users, res = manager.find_mfd_user(cid, text, rating)
        if len(users) == 1:
            bot.send_message(cid, res)
            settings(bot, update)
        if len(users) > 1:
            bot.send_message(cid, 'Найдено несколько пользователей. Уточните запрос или введите новый. Имя: Рейтинг',
                             reply_markup=keyboard_markup([f"{user[1]} : {user[3]}" for user in users], n_col=1))
        if len(users) == 0:
            bot.send_message(cid, 'Пользователь не найден. Введите новый запрос')


def mfd_add_thread(bot, update):
    text = str(update.message.text)
    cid = update.message.chat_id
    if text.startswith('http'):
        answer = manager.resolve_mfd_thread_link(cid, text)
        if answer is not None:
            bot.send_message(cid, f"Тема {answer} добавлена в подписки")
            settings(bot, update)
        else:
            bot.send_message(cid, "Тема не найдена. Проверьте ссылку и попробуйте еще раз")
    else:
        bot.send_chat_action(chat_id=cid, action=telegram.ChatAction.TYPING)
        titles, res = manager.find_mfd_thread(cid, text)
        if len(titles) == 1:
            bot.send_message(cid, res)
            settings(bot, update)
        if len(titles) > 1:
            print(titles)
            bot.send_message(cid, "Найдено несколько тем. Уточните запрос или введите новый",
                             reply_markup=keyboard_markup(titles, n_col=1))
        if len(titles) == 0:
            bot.send_message(cid, "Тема с таким именем не найдена. Введите новый запрос")


dispatcher.add_handler(CommandHandler('about', about))
dispatcher.add_handler(CommandHandler('key', key))

dispatcher.add_handler(RegexHandler('^Смартлаб топ 24 часа$', smartlab))
dispatcher.add_handler(RegexHandler('^About', about))

dispatcher.add_handler(RegexHandler('^Подписки$', settings))
dispatcher.add_handler(RegexHandler('^Текущие подписки$', print_settings))

dispatcher.add_handler(RegexHandler('^Отмена$', key))

dispatcher.add_handler(RegexHandler('^Подписаться на ALЁNKA', subscribe_alenka))
dispatcher.add_handler(RegexHandler('^Отписаться от ALЁNKA', unsubscribe_alenka))

dispatcher.add_handler(RegexHandler('^MFD.ru тема', mfd_forum))
dispatcher.add_handler(RegexHandler('^Добавить mfd тему$', mfd_forum_add))
dispatcher.add_handler(RegexHandler('^Удалить mfd тему$', mfd_forum_remove))

dispatcher.add_handler(RegexHandler('^MFD.ru пользователи', mfd_user))
dispatcher.add_handler(RegexHandler('^Добавить mfd пользователя$', mfd_user_add))
dispatcher.add_handler(RegexHandler('^Удалить mfd пользователя$', mfd_user_remove))

dispatcher.add_handler(MessageHandler(Filters.text, received_information))

j = updater.job_queue
job_minute = j.run_repeating(check_update, interval=60, first=0)
updater.start_polling()
updater.idle()
