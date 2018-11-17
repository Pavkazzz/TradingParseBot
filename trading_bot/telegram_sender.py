import logging

from aiotg import BotApiError

log = logging.getLogger(__name__)


async def send_message(manager, bot, chat_id: int, sended_id: int, message: str, message_id: int):
    try:
        if not sended_id:
            sended_msg = await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        else:
            sended_msg = await bot.edit_message_text(
                chat_id=chat_id,
                text=message,
                message_id=sended_id,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )

        logging.info('Send message: %r', sended_msg)
        if sended_msg['ok']:
            manager.set_username(chat_id, sended_msg['result']['from']['username'])
            if message_id:
                manager.set_sended_id(sended_msg['result']['message_id'], chat_id, message_id)
        else:
            log.warning('Fail to send message! %r %r %r', chat_id, message, message_id)

    except BotApiError:
        log.exception("Error BotApiError: %r", message)


# https://core.telegram.org/bots/api#deletemessage
async def remove_message(bot, chat_id, sended_id):
    if sended_id:
        await bot.api_call('deleteMessage', chat_id=chat_id, message_id=sended_id)
