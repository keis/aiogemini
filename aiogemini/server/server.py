import asyncio

from ssl import SSLContext

from .. import GEMINI_PORT
from .protocol import Protocol, _RequestHandler


class Server:
    ssl: SSLContext
    host: str
    port: int
    _request_handler: _RequestHandler

    def __init__(
        self,
        ssl: SSLContext,
        request_handler: _RequestHandler,
        host: str = '127.0.0.1',
        port: int = GEMINI_PORT
    ) -> None:
        self.ssl = ssl
        self._request_handler = request_handler
        self.host = host
        self.port = port

    async def serve(self) -> None:
        loop = asyncio.get_running_loop()
        server = await loop.create_server(
            lambda: Protocol(self._request_handler, loop=loop),
            self.host,
            self.port,
            ssl=self.ssl
        )
        async with server:
            await server.serve_forever()
