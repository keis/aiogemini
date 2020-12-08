import asyncio

from ssl import SSLContext

from .. import GEMINI_PORT
from ..security import SecurityContext
from .protocol import Protocol, _RequestHandler


class Server:
    security: SecurityContext
    host: str
    port: int
    _request_handler: _RequestHandler

    def __init__(
        self,
        security: SecurityContext,
        request_handler: _RequestHandler,
        host: str = '127.0.0.1',
        port: int = GEMINI_PORT
    ) -> None:
        self.security = security
        self._request_handler = request_handler
        self.host = host
        self.port = port

    async def serve(self) -> None:
        loop = asyncio.get_running_loop()
        ssl = self.security.get_server_ssl_context()
        server = await loop.create_server(
            lambda: Protocol(self._request_handler, loop=loop),
            self.host,
            self.port,
            ssl=ssl
        )
        async with server:
            await server.serve_forever()
