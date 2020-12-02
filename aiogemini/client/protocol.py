from __future__ import annotations

import asyncio
from typing import Optional

from yarl import URL

from .. import GEMINI_MEDIA_TYPE
from ..abstract import BaseResponse, BaseRequest

BUFFER_SIZE = 2 ** 10


class Request(BaseRequest):
    transport: Optional[asyncio.Transport]

    def start(self) -> None:
        encoded_url = str(self.url).encode('utf-8')
        self.transport.write(b"%s\r\n" % (encoded_url,))


class Response(BaseResponse):
    stream: Optional[asyncio.StreamReader]

    async def read(self, n=-1) -> bytes:
        return await self.stream.read(n)


class ResponseParser:
    stream: Optional[asyncio.StreamReader] = None

    def feed_data(self, data: bytes) -> Optional[Response]:
        if self.stream:
            self.stream.feed_data(data)
            return

        headerend = data.index(b'\r\n')
        header = data[:headerend].decode('utf-8')
        status, meta = header.split(' ', 1)
        response = Response.from_meta(int(status), meta)
        stream = asyncio.StreamReader(limit=BUFFER_SIZE)
        self.stream = response.stream = stream
        stream.feed_data(data[headerend+2:])
        return response

    def feed_eof(self) -> None:
        if self.stream:
            self.stream.feed_eof()


class Protocol(asyncio.Protocol):
    _loop: asyncio.AbstractEventLoop
    _parser: ResponseParser

    request: Request
    response: asyncio.Future[Response]

    def __init__(
        self,
        request: Request,
        *,
        loop: asyncio.AbstractEventLoop
    ) -> None:
        self._loop = loop
        self._parser = ResponseParser()
        self.request = request
        self.response = loop.create_future()

    def connection_made(self, transport: asyncio.Transport) -> None:
        self.request.transport = transport
        self.request.start()

    def connection_lost(self, exc) -> None:
        # TODO: Deal with exc
        self._parser.feed_eof()

    def data_received(self, data: bytes) -> None:
        response = self._parser.feed_data(data)
        if response:
            if response.stream:
                assert self.request.transport, "Request should have transport"
                response.stream.set_transport(self.request.transport)
            self.response.set_result(response)
