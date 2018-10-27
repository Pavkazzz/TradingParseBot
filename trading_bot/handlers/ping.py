import fast_json
from aiohttp.web_response import json_response
from aiohttp.web_urldispatcher import View


class PingHandler(View):
    async def get(self):
        return json_response(body=fast_json.dumps({'status': 'ok'}))
