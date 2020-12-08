import asyncio

from yarl import URL

from .. import GEMINI_PORT
from ..security import SecurityContext
from .protocol import Protocol, Request, Response


class Client:
    security: SecurityContext

    def __init__(self, security: SecurityContext) -> None:
        self.security = security

    async def send_request(self, request: Request) -> Response:
        loop = asyncio.get_running_loop()
        protocol = Protocol(request, loop=loop)
        if request.url.host is None:
            raise ValueError("Request must have absolute url")
        ssl = self.security.get_client_ssl_context(request.url.host)
        await loop.create_connection(
            lambda: protocol,
            request.url.host,
            request.url.port or GEMINI_PORT,
            ssl=ssl,
        )
        return await protocol.response

    async def get(self, url: URL) -> Response:
        return await self.send_request(Request(url=url))
