from aiohttp.web_urldispatcher import View
from aiotg import Bot

from trading_bot.manager import Manager


class BaseView(View):
    @property
    def manager(self) -> Manager:
        return self.request.app['manager']

    @property
    def bot(self) -> Bot:
        return self.request.app['bot']