import argparse
import asyncio
import os
import sys

from base64 import b64decode, b64encode
from pathlib import Path

from yarl import URL

from .. import Status, tofu
from . import Client


def data_home() -> Path:
    if xdgdatahome := os.environ.get('XDG_DATA_HOME'):
        base = Path(xdgdatahome)
    elif home := os.environ.get('HOME'):
        base = Path(home) / '.local' / 'share'
    else:
        raise RuntimeError("Could not identify data directory")

    return base / 'aiogemini'


def load_trust_data(trustlocation: Path) -> dict[str, bytes]:
    if trustlocation.exists():
        with trustlocation.open() as truststore:
            return {
                domain: b64decode(fingerprint)
                for domain, fingerprint
                in (line.split('\t', 1) for line in truststore.readlines())
            }

    return {}


def save_trust_data(trustlocation: Path, trust: dict[str, bytes]) -> None:
    trustlocation.parent.mkdir(parents=True, exist_ok=True)
    tmp = trustlocation.with_suffix('.tmp')
    with tmp.open('w') as truststore:
        truststore.writelines(
            '\t'.join((domain, b64encode(fingerprint).decode('utf-8'))) + '\n'
            for domain, fingerprint in trust.items())
    tmp.rename(trustlocation)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=URL)
    parser.add_argument(
        '--trust', type=argparse.FileType('w'))
    parser.add_argument(
        '--cert', type=argparse.FileType('r'))
    parser.add_argument(
        '--key', type=argparse.FileType('r'))
    args = parser.parse_args()

    trustlocation = (
        Path(args.trust.name) if args.trust else
        (data_home() / 'trust')
    )
    trust = load_trust_data(trustlocation)
    trustlen = len(trust)

    ssl = tofu.create_client_ssl_context(
        trust,
        args.cert.name if args.cert else None,
        args.key.name if args.key else None)
    client = Client(ssl)
    resp = await client.get(args.url)

    if len(trust) != trustlen:
        save_trust_data(trustlocation, trust)

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
