import pytest
import asyncio
import ssl
from unittest.mock import Mock
from hamcrest import assert_that, calling, raises

from yarl import URL
from aiogemini.client import Client


async def resolved(obj):
    fut = asyncio.ensure_future(obj)
    await asyncio.wait([fut])
    return fut


@pytest.mark.asyncio
async def test_rejects_relative_url() -> None:
    sslcontext = Mock(spec=ssl.SSLContext)
    client = Client(sslcontext)
    url = URL('/url-without-host')
    future = await resolved(client.get(url))
    assert_that(
        calling(future.result),
        raises(ValueError, pattern='absolute url'))
