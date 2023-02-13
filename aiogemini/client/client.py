import asyncio
from ssl import SSLContext

from yarl import URL

from .. import GEMINI_PORT
from .protocol import Protocol, Request, Response


class Client:
    ssl: SSLContext

    def __init__(self, ssl: SSLContext) -> None:
        self.ssl = ssl

    async def send_request(self, request: Request) -> Response:
        assert request.url.host, "URL must specify host"
        loop = asyncio.get_running_loop()
        protocol = Protocol(request, loop=loop)
        await loop.create_connection(
            lambda: protocol,
            request.url.host,
            request.url.port or GEMINI_PORT,
            ssl=self.ssl,
        )
        return await protocol.response

    async def get(self, url: URL) -> Response:
        return await self.send_request(Request(url=url))
