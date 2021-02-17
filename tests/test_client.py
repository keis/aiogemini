import pytest
import asyncio
from unittest.mock import Mock
from typing import Callable
from hamcrest import assert_that, calling, raises

from yarl import URL
from aiogemini.client import Client
from aiogemini.security import SecurityContext


async def resolved(obj):
    fut = asyncio.ensure_future(obj)
    await asyncio.wait([fut])
    return fut


@pytest.mark.asyncio
async def test_rejects_relative_url() -> None:
    sc = Mock(spec=SecurityContext)
    client = Client(sc)
    url = URL('/url-without-host')
    future = await resolved(client.get(url))
    assert_that(
        calling(future.result),
        raises(ValueError, pattern='absolute url'))
