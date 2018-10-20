import asyncio
from asyncio import WindowsProactorEventLoopPolicy

import pytest

from trading_bot.sources import AbstractSource, Page


@pytest.fixture
def event_loop():
    asyncio.set_event_loop_policy(WindowsProactorEventLoopPolicy())
    asyncio.get_event_loop().close()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        loop.close()


class TestSource(AbstractSource):
    def check_update(self, *args) -> Page:
        raise NotImplemented


pytestmark = pytest.mark.asyncio
