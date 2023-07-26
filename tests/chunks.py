from collections import deque
from itertools import islice
from typing import Iterable, Generator

from hypothesis.strategies import DrawFn, composite, integers, lists


def window(size: int, items: Iterable[int]) -> Generator[deque[int], None, None]:
    i = iter(items)
    win = deque(islice(i, size), maxlen=size)
    yield win
    for o in i:
        win.append(o)
        yield win


@composite
def chunks(draw: DrawFn, data: bytes) -> tuple[bytes, list[bytes]]:
    size = len(data)
    splits: list[int] = draw(
        lists(
            integers(min_value=0, max_value=max(size - 1, 0)),
            unique=True,
            max_size=max(size-1, 0),
        ).map(sorted)
    )
    return data, [data[a:b] for a, b in window(2, [0, *splits, size])]
