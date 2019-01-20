import asyncio

import pytest
from aioredis import Redis, create_redis_pool

from trading_bot.sources.sources import AbstractSource, Page

pytestmark = pytest.mark.asyncio


class EmptyTestSource(AbstractSource):
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


@pytest.fixture
def redis_host() -> str:
    return "redis://localhost"


@pytest.fixture
async def redis(redis_host, loop) -> Redis:
    r = await create_redis_pool(redis_host, minsize=1, maxsize=1)
    try:
        yield r
    finally:
        r.close()
        await r.wait_closed()
