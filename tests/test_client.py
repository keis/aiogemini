import pytest
import ssl
from unittest.mock import Mock
from hamcrest import assert_that, calling, raises

from yarl import URL
from aiogemini.client import Client
from .future import resolved, future_raising


@pytest.mark.asyncio
async def test_rejects_relative_url() -> None:
    sslcontext = Mock(spec=ssl.SSLContext)
    client = Client(sslcontext)
    url = URL('/url-without-host')
    assert_that(
        await resolved(client.get(url)),
        future_raising(ValueError, pattern='absolute url'))
