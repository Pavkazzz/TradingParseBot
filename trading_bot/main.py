import logging

import configargparse
from aiomisc.entrypoint import entrypoint
from aiomisc.service.raven import RavenSender
from aiomisc.service.tracer import MemoryTracer
from aiomisc.utils import bind_socket, new_event_loop

from trading_bot.services.telegram_app import TelegramWebhook
from trading_bot.services.updater_service import UpdaterService
from trading_bot.settings import sentry_key
from trading_bot.telegram_handlers import init

log = logging.getLogger(__name__)

p = configargparse.ArgParser(
    auto_env_var_prefix='APP_'
)
p.add_argument('--redis-url', default='127.0.0.1', help='Url for redis database', type=str)
p.add_argument('--host-url', required=True)

p.add_argument('--memory-tracer', action="store_true", default=False)

if __name__ == '__main__':
    arguments = p.parse_args()

    loop = new_event_loop()
    bot, manager = loop.run_until_complete(init(arguments.redis_url))

    socket = bind_socket(
        address='0.0.0.0',
        port=80,
        proto_name='http'
    )

    services = [
        TelegramWebhook(
            sock=socket,
            bot=bot,
            manager=manager,
            host=arguments.host_url
        ),
        UpdaterService(
            bot=bot,
            manager=manager,
        ),
        RavenSender(sentry_dsn=sentry_key)
    ]
    if arguments.memory_tracer:
        services.append(MemoryTracer(interval=60))

    with entrypoint(loop=loop, *services) as loop:
        log.info('Start')
        loop.run_forever()
