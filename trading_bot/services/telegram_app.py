import logging

from aiohttp.web_app import Application
from aiomisc.service.aiohttp import AIOHTTPService
from aiotg import Bot

from trading_bot.handlers.ping import PingHandler
from trading_bot.settings import dev_hooks_token

log = logging.getLogger(__name__)


class TelegramWebhook(AIOHTTPService):
    bot: Bot = None
    ssl_cert = None

    async def create_application(self):
        print(await self.bot.api_call('getWebhookInfo'))
        await self.bot.set_webhook(
            webhook_url=f'https://pavkazzz.ru/webhook/{dev_hooks_token}'
        )
        app: Application = self.bot.create_webhook_app(f'/webhook/{dev_hooks_token}')
        app.router.add_route('GET', '/api/v1/ping', PingHandler)
        return app

