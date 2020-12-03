import asyncio
import ssl

from .. import Status, GEMINI_PORT
from . import Server, Request, Response


async def hello(req: Request) -> Response:
    return Response(Status.NOT_FOUND)


async def hello2(req: Request) -> Response:
    async def world() -> None:
        await asyncio.sleep(2)
        response.write(b"world!")
        response.write_eof()

    loop = asyncio.get_running_loop()
    loop.create_task(world())

    response = Response(Status.SUCCESS)
    response.start(req)
    response.write(b"Hallo, ")

    return response


async def main():
    loop = asyncio.get_running_loop()

    sslcontext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    sslcontext.check_hostname = False
    sslcontext.load_cert_chain('localhost.crt', 'localhost.key')

    server = Server(
        sslcontext,
        hello
    )
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
