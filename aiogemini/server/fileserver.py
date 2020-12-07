from pathlib import Path, PurePath

from .. import Status
from . import _RequestHandler, Request, Response


def create_fileserver(
    root: Path,
    buffersize: int = 2 ** 20
) -> _RequestHandler:
    async def handle_request(req: Request) -> Response:
        target = root / req.url.path.lstrip('/')
        try:
            with target.open('rb') as f:
                response = Response()
                response.start(req)
                while data := f.read(buffersize):
                    await response.write(data)
                await response.write_eof()
                return response
        except IsADirectoryError:
            listing = []
            for path in target.iterdir():
                listing.append(f"=> {path.name}")
            return Response(data='\n'.join(listing).encode('utf-8'))

        except FileNotFoundError:
            return Response(Status.NOT_FOUND, "No such file")

    return handle_request
