import asyncio
import ssl

from .. import Status, GEMINI_PORT
from . import Server, Request, Response


async def hello(req: Request) -> Response:
    return Response(Status.NOT_FOUND)


async def hello2(req: Request) -> Response:
    async def world() -> None:
        await asyncio.sleep(2)
        await response.write(b"world!")
        await response.write_eof()

    loop = asyncio.get_running_loop()
    loop.create_task(world())

    response = Response(Status.SUCCESS)
    response.start(req)
    response.write(b"Hallo, ")

    return response


async def vom(req: Request) -> Response:
    async def write() -> None:
        for x in range(2 ** 14):
            await response.write(data)
        await response.write_eof()
        print("KBYE")

    data = ("X" * (2 ** 8)).encode('utf-8')

    loop = asyncio.get_running_loop()
    loop.create_task(write())

    response = Response(Status.BAD_REQUEST)
    response.start(req)

    return response


async def main():
    loop = asyncio.get_running_loop()

    sslcontext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    sslcontext.check_hostname = False
    sslcontext.load_cert_chain('localhost.crt', 'localhost.key')

    server = Server(
        sslcontext,
        vom
    )
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
