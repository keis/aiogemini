import asyncio
import ssl

from yarl import URL

from .. import GEMINI_PORT
from .protocol import Protocol, Request


async def main():
    loop = asyncio.get_running_loop()

    sslcontext = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    sslcontext.check_hostname = False
    sslcontext.load_verify_locations('localhost.crt')

    request = Request.from_str('gemini://localhost')
    protocol = Protocol(request, loop=loop)
    transport, _ = await loop.create_connection(
        lambda: protocol,
        '127.0.0.1',
        GEMINI_PORT,
        ssl=sslcontext
    )

    resp = await protocol.response
    print("header", resp)
    while True:
        data = await resp.stream.read(2 ** 6)
        print("data", data)
        if len(data) == 0:
            break


if __name__ == '__main__':
    asyncio.run(main())
