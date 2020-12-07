import asyncio
import ssl

from pathlib import Path

from .. import Status, GEMINI_PORT
from . import Server, Request, Response

from .fileserver import create_fileserver


async def main():
    loop = asyncio.get_running_loop()

    sslcontext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    sslcontext.check_hostname = False
    sslcontext.load_cert_chain('localhost.crt', 'localhost.key')

    server = Server(
        sslcontext,
        create_fileserver(Path.cwd())
    )
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
