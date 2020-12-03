import argparse
import asyncio

from yarl import URL

from .. import GEMINI_PORT
from ..security import TOFUContext
from . import Client


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=URL)
    args = parser.parse_args()

    certs = {}
    client = Client(TOFUContext(certs))
    resp = await client.get(args.url)

    print("header", resp)
    while True:
        data = await resp.read(2 ** 6)
        print("data", data)
        if len(data) == 0:
            break


if __name__ == '__main__':
    asyncio.run(main())
