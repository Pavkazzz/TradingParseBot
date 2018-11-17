import fast_json
from aiohttp.web_response import Response

from trading_bot.handlers.baseview import BaseView


class SendHandler(BaseView):
    async def post(self):
        json = await self.request.json(loads=fast_json.loads)
        await self.manager.send_to_all_users(json["text"])
        return Response(body="ok")
