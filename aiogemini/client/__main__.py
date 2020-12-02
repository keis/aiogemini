import argparse
import asyncio
import ssl

from yarl import URL

from .. import GEMINI_PORT
from . import Client


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=URL)
    args = parser.parse_args()

    # FIXME
    sslcontext = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    sslcontext.check_hostname = False
    sslcontext.verify_mode = ssl.CERT_NONE
    sslcontext.load_verify_locations('localhost.crt')

    client = Client(sslcontext)
    resp = await client.get(args.url)

    print("header", resp)
    while True:
        data = await resp.read(2 ** 6)
        print("data", data)
        if len(data) == 0:
            break


if __name__ == '__main__':
    asyncio.run(main())
