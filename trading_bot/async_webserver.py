import logging

import configargparse
import requests_cache
from aiomisc.entrypoint import entrypoint
from aiomisc.utils import bind_socket
from redis import Redis

from trading_bot.manager import Manager
from trading_bot.services.telegram_app import TelegramWebhook
from trading_bot.services.updater_service import UpdaterService
from trading_bot.telegram_handlers import MessageHandler

log = logging.getLogger(__name__)

p = configargparse.ArgParser(
    auto_env_var_prefix='APP'
)
p.add_argument('--redis-url', default='127.0.0.1', help='Url for redis database', type=str)
arguments = p.parse_args()

redis = Redis(host=arguments.redis_url)
if redis.ping():
    log.info('Success connect to redis')
else:
    log.info('Cannot connect to redis!')

requests_cache.install_cache('click_cache', backend='redis', connection=redis)

socket = bind_socket(
    address='0.0.0.0',
    port=80,
    proto_name='http'
)

manager = Manager()
mess = MessageHandler(manager)

services = [
    TelegramWebhook(
        sock=socket,
        bot=mess.bot,
        manager=manager,
    ),
    UpdaterService(bot=mess.bot, manager=manager)
]


@mess.bot.command(r"/echo (.+)")
def echo(chat, match):
    log.info('Incoming message %r', chat)
    return chat.reply(match.group(1))


with entrypoint(*services) as loop:
    log.info('Start')
    loop.run_forever()
