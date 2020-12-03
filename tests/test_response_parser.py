from typing import List, Optional

from hamcrest import assert_that, instance_of, equal_to, calling, raises
from hypothesis import given
from hypothesis.strategies import text, just

from aiogemini import Status
from aiogemini.client.protocol import Response, ResponseParser

from .chunks import chunks

RESPONSE =  b'20 text/plain\r\nThis is some very interesting content'


def test_parse_simple_response():
    parser = ResponseParser()

    res = parser.feed_data(RESPONSE)

    assert res, "Should parse resuest"
    print(res)
    assert_that(res, instance_of(Response))
    assert_that(res.status, equal_to(Status.SUCCESS))
    assert_that(res.content_type, equal_to('text/plain'))

    assert res.stream, "Should have stream"


@given(
    just(RESPONSE).flatmap(chunks)
)
def test_chunk_input(input):
    data, chunks = input
    parser = ResponseParser()

    res: Optional[Response] = None
    for chunk in chunks:
        r = parser.feed_data(chunk)
        if res:
            assert_that(r, equal_to(None))
        else:
            res = r
    parser.feed_eof()

    assert res, "Should parse resuest"
    assert_that(res, instance_of(Response))
    assert_that(res.status, equal_to(Status.SUCCESS))
    assert_that(res.content_type, equal_to('text/plain'))
