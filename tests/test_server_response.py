import pytest
from asyncio import (
    Protocol,
    Transport,
    AbstractEventLoop as Loop,
    get_event_loop
)
from asynctest import Mock, CoroutineMock
from matchmock import called_once, called_with
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    has_property,
    raises,
)
from yarl import URL

from aiogemini import Status
from aiogemini.server import Request, Response


@pytest.fixture
def loop() -> Loop:
    return get_event_loop()


@pytest.fixture
def transport() -> Transport:
    return Mock(spec=Transport)


@pytest.fixture
def protocol(loop: Loop, transport: Transport) -> Protocol:
    protocol = Mock(transport=transport)
    protocol._drain_helper = CoroutineMock()
    return protocol


def test_writes_payload_when_started(
    protocol: Protocol,
    transport: Transport,
    loop: Loop
) -> None:
    data = b'somedata'
    header = b'20 text/gemini; charset=utf-8\r\n'
    res = Response(data=data)
    res._start(transport, protocol, loop)
    assert_that(transport.write, called_with(header))
    assert_that(transport.write, called_with(data))
    assert_that(transport.close, called_once())


def test_closes_when_started_with_error(
    protocol: Protocol,
    transport: Transport,
    loop: Loop
) -> None:
    header = b'59 BAD_REQUEST\r\n'
    res = Response(status=Status.BAD_REQUEST)
    res._start(transport, protocol, loop)
    assert_that(transport.write, called_with(header))
    assert_that(transport.close, called_once())
    res.write(b'more data')


@pytest.mark.asyncio
async def test_drain(
    protocol: Protocol,
    transport: Transport,
    loop: Loop
) -> None:
    res = Response()
    res._start(transport, protocol, loop)
    await res.drain()
    assert_that(protocol, has_property('_drain_helper', called_once()))


def test_multiple_responses_disallowed(
    protocol: Protocol,
    transport: Transport,
    loop: Loop
) -> None:
    req = Request(url=URL())
    req.transport = transport
    req.protocol = protocol
    res1 = Response()
    res1.start(req, loop=loop)
    res2 = Response()
    assert_that(
        calling(res2.start).with_args(req, loop=loop),
        raises(RuntimeError))
