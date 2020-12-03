from typing import List

from hamcrest import assert_that, instance_of, equal_to, calling, raises
from hypothesis import given
from hypothesis.strategies import text, just

from aiogemini.server.protocol import Request, RequestParser

from .chunks import chunks

REQUEST = b'gemini://some.host/some.path\r\n'


def test_parse_simple_request():
    parser = RequestParser()

    req = parser.feed_data(REQUEST)
    parser.feed_eof()

    assert req, "Should parse request"
    assert_that(req, instance_of(Request))
    assert_that(req.url.scheme, equal_to('gemini'))
    assert_that(req.url.host, equal_to('some.host'))
    assert_that(req.url.path, equal_to('/some.path'))


@given(
    just(REQUEST).flatmap(chunks)
)
def test_chunk_input(input):
    data, chunks = input
    *partial, tail = chunks
    parser = RequestParser()


    for chunk in partial:
        req = parser.feed_data(chunk)
        assert_that(req, equal_to(None))
    req = parser.feed_data(tail)
    parser.feed_eof()

    assert req, "Should parse request"
    assert_that(req, instance_of(Request))
    assert_that(req.url.scheme, equal_to('gemini'))
    assert_that(req.url.host, equal_to('some.host'))
    assert_that(req.url.path, equal_to('/some.path'))
