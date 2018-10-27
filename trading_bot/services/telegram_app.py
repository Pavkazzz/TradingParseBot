import logging

from aiohttp.web_app import Application
from aiomisc.service.aiohttp import AIOHTTPService
from aiotg import Bot

from trading_bot.handlers.ping import PingHandler
from trading_bot.handlers.send import SendHandler
from trading_bot.handlers.users import UserHandler
from trading_bot.manager import Manager
from trading_bot.settings import dev_hooks_token

log = logging.getLogger(__name__)


class TelegramWebhook(AIOHTTPService):
    bot: Bot = None
    manager: Manager = None

    async def create_application(self):
        log.info(await self.bot.api_call('getWebhookInfo'))
        await self.bot.set_webhook(
            webhook_url=f'https://pavkazzz.ru/webhook/{dev_hooks_token}'
        )
        app: Application = self.bot.create_webhook_app(f'/webhook/{dev_hooks_token}')
        app.router.add_route('GET', '/api/v1/ping', PingHandler)
        app.router.add_route('GET', '/api/v1/users', UserHandler)
        app.router.add_route('POST', '/api/v1/send', SendHandler)

        app['manager'] = self.manager
        app['bot'] = self.bot

        return app
