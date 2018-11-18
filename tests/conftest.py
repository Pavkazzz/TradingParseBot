import asyncio

import pytest

from trading_bot.sources.sources import AbstractSource, Page

pytestmark = pytest.mark.asyncio


class TestSource(AbstractSource):
    def check_update(self, *args) -> Page:
        raise NotImplemented


@pytest.fixture
async def event_loop():
    asyncio.get_event_loop().close()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        loop.close()
