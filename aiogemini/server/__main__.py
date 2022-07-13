import asyncio
import argparse

from pathlib import Path

from .. import tofu
from . import Server

from .fileserver import create_fileserver


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--cert', type=argparse.FileType('r'), required=True)
    parser.add_argument(
        '--key', type=argparse.FileType('r'), required=True)
    args = parser.parse_args()

    ssl = tofu.create_server_ssl_context(args.cert.name, args.key.name)

    server = Server(
        ssl,
        create_fileserver(Path.cwd())
    )
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
