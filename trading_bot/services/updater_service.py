import itertools
import logging

from aiomisc.periodic import PeriodicCallback
from aiomisc.service import Service

from trading_bot.telegram_sender import send_message

log = logging.getLogger(__name__)


class UpdaterService(Service):
    manager = None
    bot = None

    async def start(self):
        pc = PeriodicCallback(self.check_update)
        pc.start(30)

    def grouper(self, n, iterable, fillvalue=None):
        args = [iter(iterable)] * n
        return itertools.zip_longest(fillvalue=fillvalue, *args)

    async def check_update(self):
        async for chat_id, data in self.manager.check_new_all():
            for singlepost, message_id in data:
                await send_message(
                    self.manager,
                    self.bot,
                    chat_id,
                    message_id,
                    singlepost.format(),
                    singlepost.id,
                )
