import argparse
import asyncio
import sys

from yarl import URL

from .. import GEMINI_PORT, Status
from ..security import TOFUContext
from . import Client


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=URL)
    args = parser.parse_args()

    certs = {}
    client = Client(TOFUContext(certs))
    resp = await client.get(args.url)

    if resp.status == Status.SUCCESS:
        while True:
            data = await resp.read(2 ** 10)
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
            if len(data) == 0:
                break
    else:
        print(f"{resp.status.name}: {resp.reason}", file=sys.stderr)
        sys.exit(resp.status.value)


if __name__ == '__main__':
    asyncio.run(main())
