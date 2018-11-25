import fast_json
from aiohttp.web_response import json_response

from trading_bot.handlers.baseview import BaseView


class UserHandler(BaseView):
    async def get(self):
        return json_response(
            data={"users": self.manager.users_subscription},
            dumps=fast_json.dumps
        )
