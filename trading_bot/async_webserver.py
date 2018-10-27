import logging

from aiomisc.entrypoint import entrypoint
from aiomisc.utils import bind_socket
from aiotg import Bot

from trading_bot.manager import Manager
from trading_bot.services.telegram_app import TelegramWebhook
from trading_bot.settings import dev_hooks_token, chatbase_token, proxy_string

log = logging.getLogger(__name__)

SSL_CERT = '/etc/nginx/certs/certificate.pem'

socket = bind_socket(
    address='0.0.0.0',
    port=80,
    proto_name='http'
)

bot = Bot(
    api_token=dev_hooks_token,
    chatbase_token=chatbase_token,
    name='TradingNewsBot',
    proxy=proxy_string
)

manager = Manager()


services = [
    TelegramWebhook(
        sock=socket,
        bot=bot,
        manager=manager,
        ssl_cert=SSL_CERT
    ),
    # UpdaterService(bot=bot, manager=manager)
]


@bot.command(r"/echo (.+)")
def echo(chat, match):
    log.info('Incoming message %r', chat)
    return chat.reply(match.group(1))


with entrypoint(*services) as loop:
    log.info('Start')
    loop.run_forever()
