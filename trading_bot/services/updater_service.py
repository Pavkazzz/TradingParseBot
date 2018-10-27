import logging

from aiomisc.periodic import PeriodicCallback
from aiomisc.service import Service
from aiotg import BotApiError

log = logging.getLogger(__name__)


class UpdaterService(Service):
    manager = None
    bot = None

    async def start(self):
        pc = PeriodicCallback(self.check_update)
        pc.start(60)

    async def check_update(self):
        async for chat_id, data in self.manager.check_new_all():
            for singlepost, message_id in data:
                try:
                    if not message_id:
                        sended_msg = await self.bot.send_message(
                            chat_id=chat_id,
                            text=singlepost.format(),
                            parse_mode='Markdown',
                            disable_web_page_preview=True
                        )
                    else:
                        sended_msg = await self.bot.edit_message_text(
                            chat_id=chat_id,
                            text=singlepost.format(),
                            message_id=message_id,
                            parse_mode='Markdown',
                            disable_web_page_preview=True
                        )

                    logging.info('Send message: %r', sended_msg)
                    self.manager.set_message_id(sended_msg['result']['message_id'], chat_id, singlepost.id)

                except BotApiError:
                    logging.exception("Error BotApiError: %r", singlepost)
