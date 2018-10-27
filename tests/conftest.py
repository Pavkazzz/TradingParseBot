import asyncio
import os
# from asyncio import WindowsProactorEventLoopPolicy

import pytest
import requests_cache
from redis import Redis

from trading_bot.sources import AbstractSource, Page

pytestmark = pytest.mark.asyncio


class TestSource(AbstractSource):
    def check_update(self, *args) -> Page:
        raise NotImplemented


@pytest.fixture
async def event_loop():
    # asyncio.set_event_loop_policy(WindowsProactorEventLoopPolicy())
    asyncio.get_event_loop().close()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        loop.close()


requests_cache.install_cache('click_cache', backend='redis', connection=Redis(host='127.0.0.1'))
