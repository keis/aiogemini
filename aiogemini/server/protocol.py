from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Optional

from yarl import URL

from .. import Status, GEMINI_MEDIA_TYPE
from ..abstract import BaseRequest, BaseResponse


class Request(BaseRequest):
    transport: Optional[asyncio.Transport] = \
        field(default=None, init=False, repr=False)
    protocol: Optional[Protocol] = field(default=None, init=False, repr=False)


@dataclass
class Response(BaseResponse):
    data: Optional[bytes] = None
    stream: Optional[asyncio.StreamWriter] = field(default=None, repr=False)

    @property
    def has_started(self) -> bool:
        return self.stream is not None

    def _start(
        self,
        transport: asyncio.Transport,
        protocol: asyncio.Protocol,
        loop: asyncio.AbstractEventLoop
    ) -> None:
        self.stream = asyncio.StreamWriter(transport, protocol, None, loop)
        self.stream.write(
            f"{self.status.value} {self.meta}\r\n".encode('utf-8'))

        if self.status != Status.SUCCESS:
            self.stream.close()

        if self.data:
            self.stream.write(self.data)
            self.stream.close()

    def start(self, request: Request) -> None:
        assert request.protocol, "Request should have a protocol"
        assert request.transport, "Request should have a transport"
        self._start(
            request.transport,
            request.protocol,
            request.protocol._loop
        )

    async def write(self, data: bytes) -> None:
        self.stream.write(data)
        await self.drain()

    async def write_eof(self) -> None:
        self.stream.close()
        await self.drain()

    async def drain(self) -> None:
        await self.stream.drain()


_RequestHandler = Callable[[Request], Awaitable[Response]]


class RequestParser:
    buffer: Optional[bytes] = bytes()

    def feed_data(self, data: bytes) -> Optional[Request]:
        if self.buffer is None:
            raise ValueError("Parser is closed")

        self.buffer += data
        try:
            end = self.buffer.index(b'\r\n')
        except ValueError:
            return None

        line = self.buffer[:end]
        self.buffer = None

        return Request(
            url=URL(line.decode('utf-8'))
        )

    def feed_eof(self) -> None:
        # TODO: Warn on partial input
        pass


class Protocol(asyncio.streams.FlowControlMixin):
    transport: Optional[asyncio.Transport]

    _loop: asyncio.AbstractEventLoop
    _request_handler: Optional[_RequestHandler]
    _parser: RequestParser

    def __init__(
        self,
        request_handler: Optional[_RequestHandler],
        *,
        loop: asyncio.AbstractEventLoop
    ) -> None:
        super().__init__()
        self._loop = loop
        self._request_handler = request_handler
        self._parser = RequestParser()

    def connection_made(self, transport: asyncio.Transport) -> None:
        # TODO: Check for ssl enabled
        self.transport = transport

    def connection_lost(self, exc) -> None:
        super().connection_lost(exc)
        # TODO: Deal with exc
        self._parser.feed_eof()

    def data_received(self, data: bytes) -> None:
        request = self._parser.feed_data(data)
        if request:
            # TODO: Ignore any other data
            task = self._loop.create_task(self.process_request(request))
            task.add_done_callback(lambda fut: fut.result())

    async def process_request(self, request: Request) -> None:
        print("Processing request", request)
        request_handler = self._request_handler
        assert request_handler is not None, "Needs request handler"
        request.protocol = self
        request.transport = self.transport

        response = await request_handler(request)
        if not response.has_started:
            response.start(request)
