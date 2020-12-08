import asyncio
import ssl

from pathlib import Path

from .. import Status, GEMINI_PORT
from ..security import TOFUContext
from . import Server, Request, Response

from .fileserver import create_fileserver


async def main():
    loop = asyncio.get_running_loop()

    certs = {}
    security = TOFUContext(certs, 'localhost.crt', 'localhost.key')

    server = Server(
        security,
        create_fileserver(Path.cwd())
    )
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
