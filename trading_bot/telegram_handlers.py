import logging

from aiotg import bot

log = logging.getLogger(__name__)


@bot.command(r"/echo (.+)")
def echo(chat, match):
    log.info('Incoming message %r', chat)
    return chat.reply(match.group(1))
