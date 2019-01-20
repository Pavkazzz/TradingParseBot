import logging
from hashlib import blake2b

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
    host: str = None
    webhooks_port: int = None

    async def create_application(self):
        log.info(await self.bot.api_call("getWebhookInfo"))
        url = blake2b(dev_hooks_token.encode("utf-8")).hexdigest()
        await self.bot.set_webhook(
            webhook_url=f"https://{self.host}:{self.webhooks_port}/webhook/{url}"
        )
        app: Application = self.bot.create_webhook_app(f"/webhook/{url}")
        app.router.add_route("GET", "/api/v1/ping", PingHandler)
        app.router.add_route("GET", "/api/v1/users", UserHandler)
        app.router.add_route("POST", "/api/v1/send", SendHandler)

        app["manager"] = self.manager
        app["bot"] = self.bot

        return app
