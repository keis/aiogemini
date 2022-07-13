import pytest
import asyncio
import ssl
from asyncio import start_server, open_connection, ensure_future, wait
from base64 import b64decode
from hamcrest import assert_that, equal_to, has_length, has_entry, calling, raises

from aiogemini import tofu

EXPECTED_FINGERPRINT = b64decode('7i2jMtUOmFtzRO3nnc5k8sYSnS1w22WhYcF3wlXex/U=')


async def echo_server(reader, writer) -> None:
    data = await reader.read(16)
    writer.write(data)
    await writer.drain()
    writer.close()


async def hello(host, port, ssl) -> None:
    reader, writer = await open_connection(host='localhost', port=port, ssl=ssl)
    writer.write(b"hello")
    await writer.drain()
    data = await reader.read(16)
    assert_that(data, equal_to(b"hello"))


async def resolved(obj):
    fut = asyncio.ensure_future(obj)
    await asyncio.wait([fut])
    return fut


@pytest.mark.asyncio
async def test_ssl_context():
    trust = {}
    serverssl = tofu.create_server_ssl_context('tests/localhost.crt', 'tests/localhost.key')
    clientssl = tofu.create_client_ssl_context(trust, None, None)

    server = await start_server(echo_server, host='localhost', port=0, ssl=serverssl)
    port = server.sockets[0].getsockname()[1]

    await hello('localhost', port, clientssl)
    server.close()

    assert_that(trust, has_length(1))
    assert_that(trust, has_entry('localhost', EXPECTED_FINGERPRINT))



@pytest.mark.asyncio
async def test_ssl_context_fingerprint_mismatch():
    trust = { 'localhost': EXPECTED_FINGERPRINT[:-1] + b'\x00' }
    serverssl = tofu.create_server_ssl_context('tests/localhost.crt', 'tests/localhost.key')
    clientssl = tofu.create_client_ssl_context(trust, None, None)

    server = await asyncio.start_server(echo_server, host='localhost', port=0, ssl=serverssl)
    port = server.sockets[0].getsockname()[1]

    future = await resolved(hello('localhost', port, clientssl))
    server.close()

    assert_that(calling(future.result), raises(ssl.SSLCertVerificationError))
