import asyncio
import logging
from asyncio import get_event_loop

import fast_json
import telegram
from aiomisc.entrypoint import entrypoint
from aiomisc.log import basic_config
from aiomisc.periodic import PeriodicCallback
from aiomisc.utils import new_event_loop
from aiotg import Bot, Chat, BotApiError

from trading_bot.manager import Manager
from trading_bot.settings import dev_token, botan_token, proxy_string
from trading_bot.sources import SmartLab, AlenkaNews
from trading_bot.telegram_helper import build_menu, keyboard_markup

basic_config(level=logging.INFO, buffered=False, log_format='color')

IDLE, MFD_USER_ADD, MFD_USER_REMOVE, MFD_THREAD_ADD, MFD_THREAD_REMOVE = range(5)
state = IDLE

bot = Bot(
    api_token=dev_token,
    json_deserialize=fast_json.loads,
    json_serialize=fast_json.dumps,
    botan_token=botan_token,
    name='TradingNewsBot',
    proxy=proxy_string
)

manager = Manager()




@bot.command(r'/start')
def start(chat: Chat, match):
    manager.start(chat.message["from"]["id"])
    key(chat, match)


@bot.command(r'/stop')
def stop(chat: Chat, match):
    manager.stop(chat.message["from"]["id"])
    key(chat, match)


@bot.command(r'^About$')
@bot.command(r'/about')
def about(chat: Chat, match):
    chat.send_text("Привет. Я бот для оповещения. Не обижайте меня, я буду верно вам служить. \n"
                   "Умею подписываться на пользователей и темы на форуме mfd.ru и оповещать о новых сообщениях\n"
                   "Могу сообщить, когда появляется новая тема или новость на Алёнке. \n"
                   "Пользуйтесь на здоровье!")


# Начальная настройка клавиатуры
@bot.command(r'^Отмена$')
@bot.command(r'/key')
def key(chat: Chat, match):
    options = ["Подписки", "About"]
    reply_markup = build_menu(options, n_cols=2, header_buttons=["Смартлаб топ 24 часа"])
    chat.send_text("Hey!", reply_markup=reply_markup)


@bot.command(r'^Смартлаб топ 24 часа$')
async def smartlab(chat: Chat, match):
    sl = SmartLab()
    posts = await sl.check_update()
    chat.send_text(
        posts.posts[0].format(),
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )


@bot.command(r'^Подписки$')
def settings(chat: Chat, match=None):
    global state
    state = IDLE

    if manager.settings(chat.message["from"]["id"]).alenka:
        alenka = "Отписаться от ALЁNKA"
    else:
        alenka = "Подписаться на ALЁNKA"

    options = [alenka, "MFD.ru тема", "MFD.ru пользователи"]
    chat.send_text('Управление подписками', reply_markup=keyboard_markup(options, ["Текущие подписки"], 3))


@bot.command(r'^Текущие подписки$')
def print_settings(chat: Chat, match):
    chat_id = chat.message["from"]["id"]
    current_settings = manager.settings(chat_id)
    msg = ""

    if current_settings.alenka or len(current_settings.mfd_user) > 0 or len(current_settings.mfd_thread) > 0:
        msg += "Вы подписаны на:\n"
    else:
        chat.send_text("У вас нет активных подписок.", parse_mode=telegram.ParseMode.MARKDOWN)
        return

    if current_settings.alenka:
        msg += "  Новости с [https://alenka.capital](alenka.capital)\n\n"

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

    chat.send_text(msg, parse_mode=telegram.ParseMode.MARKDOWN)


@bot.command(r'^Подписаться на ALЁNKA$')
async def subscribe_alenka(chat: Chat, match):
    text, _ = await manager.new_command(chat.message["from"]["id"], Manager.ADD_ALENKA)
    chat.send_text(text)
    settings(chat, match)


@bot.command(r'^Отписаться от ALЁNKA$')
async def unsubscribe_alenka(chat: Chat, match):
    text, _ = await manager.new_command(chat.message["from"]["id"], Manager.REMOVE_ALENKA)
    chat.send_text(text)
    settings(chat, match)


@bot.command(r'^MFD.ru тема')
def mfd_forum(chat: Chat, match):
    options = ["Добавить mfd тему", "Удалить mfd тему"]
    chat.send_text("Выберете действие: ", reply_markup=keyboard_markup(options))


@bot.command(r'^Добавить mfd тему$')
def mfd_forum_add(chat: Chat, match):
    chat.send_text("Введите имя темы или ссылку на тему или любое сообщение этой темы ",
                   reply_markup=keyboard_markup())
    global state
    state = MFD_THREAD_ADD


@bot.command(r'^Удалить mfd тему$')
def mfd_forum_remove(chat: Chat, match):
    chat_id = chat.message["from"]["id"]
    chat.send_text("Выберете тему для удаления: ",
                   reply_markup=keyboard_markup(
                       [data.name for data in manager.settings(chat_id).mfd_thread], n_col=1)
                   )
    global state
    state = MFD_THREAD_REMOVE


@bot.command(r'^MFD.ru пользователи')
def mfd_user(chat: Chat, match):
    options = ["Добавить mfd пользователя", "Удалить mfd пользователя"]
    chat.send_text("Выберете действие: ", reply_markup=keyboard_markup(options))


@bot.command(r'^Добавить mfd пользователя$')
def mfd_user_add(chat: Chat, match):
    chat.send_text("Введите имя темы или ссылку на пользователя.\nЕсли передумали, введите \"Отмена\" ",
                   reply_markup=keyboard_markup())
    global state
    state = MFD_USER_ADD


@bot.command(r'^Удалить mfd пользователя$')
def mfd_user_remove(chat: Chat, match):
    chat_id = chat.message["from"]["id"]
    chat.send_text("Выберете пользователя для удаления: ",
                   reply_markup=keyboard_markup(
                       [data.name for data in manager.settings(chat_id).mfd_user], n_col=1)
                   )
    global state
    state = MFD_USER_REMOVE


@bot.default
async def received_information(chat: Chat, match):
    if state == IDLE:
        return
    if state == MFD_THREAD_ADD:
        await mfd_add_thread(chat)
    if state == MFD_THREAD_REMOVE:
        await mfd_remove_thread(chat)
    if state == MFD_USER_ADD:
        await mfd_add_user(chat)
    if state == MFD_USER_REMOVE:
        await mfd_remove_user(chat)


async def mfd_remove_user(chat: Chat):
    text = str(chat.message['text'])
    cid = chat.message["from"]["id"]
    res = ""
    for data in manager.settings(cid).mfd_user:
        if data.name == text:
            res, _ = await manager.new_command(cid, Manager.REMOVE_MFD_USER, data)
    if res:
        chat.send_text(res)
        settings(chat)
    else:
        chat.send_text("Данный пользователь не найден для удаления. Введите правильное имя")


async def mfd_remove_thread(chat: Chat):
    text = str(chat.message['text'])
    cid = chat.message["from"]["id"]
    res = ""
    for data in manager.settings(cid).mfd_thread:
        if data.name == text:
            res, _ = await manager.new_command(cid, Manager.REMOVE_MFD_THREAD, data)

    if res:
        chat.send_text(res)
        settings(chat)
    else:
        chat.send_text("Данная тема не найдена для удаления. Попробуйте еще раз")


async def mfd_add_user(chat: Chat):
    text = str(chat.message['text'])
    rating = -1
    if ': ' in text:
        try:
            spl = text.split(':')
            text = str(spl[0]).strip()
            rating = int(spl[1])
        except Exception:
            rating = 0

    cid = chat.message["from"]["id"]
    if text.startswith('http'):
        answer = await manager.resolve_mfd_user_link(cid, text)
        if not answer:
            chat.send_text(f"Пользователь {answer} добавлен в подписки")
            settings(chat)
        else:
            chat.send_text("Пользователь не найден. Проверьте ссылку и попробуйте еще раз")
    else:
        chat.send_chat_action(telegram.ChatAction.TYPING)
        users, res = await manager.find_mfd_user(cid, text, rating)
        if len(users) == 1:
            chat.send_text(res)
            settings(chat)
        if len(users) > 1:
            chat.send_text('Найдено несколько пользователей. Уточните запрос или введите новый. Имя: Рейтинг',
                           reply_markup=keyboard_markup([f"{user[1]} : {user[3]}" for user in users], n_col=1))
        if len(users) == 0:
            chat.send_text('Пользователь не найден. Введите новый запрос')


async def mfd_add_thread(chat: Chat):
    text = str(chat.message['text'])
    cid = chat.message["from"]["id"]

    if text.startswith('http'):
        answer = await manager.resolve_mfd_thread_link(cid, text)
        if answer is not None:
            chat.send_text(f"Тема {answer} добавлена в подписки")
            settings(chat)
        else:
            chat.send_text("Тема не найдена. Проверьте ссылку и попробуйте еще раз")
    else:
        chat.send_chat_action(telegram.ChatAction.TYPING)
        titles, res = await manager.find_mfd_thread(cid, text)
        if len(titles) == 1:
            chat.send_text(res)
            settings(chat)
        if len(titles) > 1:
            chat.send_text("Найдено несколько тем. Уточните запрос или введите новый",
                           reply_markup=keyboard_markup(titles, n_col=1))
        if len(titles) == 0:
            chat.send_text("Тема с таким именем не найдена. Введите новый запрос")


async def check_update():
    async for chat_id, data in manager.check_new_all():
        for singlepost, message_id in data:
            try:
                if message_id == 0:
                    sended_msg = bot.send_message(chat_id=chat_id, text=singlepost.format(),
                                                  parse_mode=telegram.ParseMode.MARKDOWN,
                                                  disable_web_page_preview=True)
                else:
                    sended_msg = bot.edit_message_text(chat_id=chat_id, text=singlepost.format(), message_id=message_id,
                                                       parse_mode=telegram.ParseMode.MARKDOWN,
                                                       disable_web_page_preview=True)

                manager.set_message_id(sended_msg.message_id, chat_id, singlepost.id)

            except BotApiError:
                logging.exception("Error BotApiError: %r", singlepost)


loop = new_event_loop()


async def update_manager():

    print(asyncio.get_event_loop().is_closed())
    a = AlenkaNews()
    p = await a.check_update()
    print(p)

    # manager.recreate_users(bot=dispatcher.bot)
    async for _ in manager.check_new_all():
        pass

if __name__ == '__main__':
    print('started')
    loop.run_until_complete(update_manager())

    per = PeriodicCallback(check_update)
    per.start(60, loop)

    bot.run(debug=True, reload=False)
