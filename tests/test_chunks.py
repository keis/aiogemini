from hypothesis import given
from hypothesis.strategies import binary
from hamcrest import assert_that, equal_to

from .chunks import chunks

@given(binary().flatmap(chunks))
def test_chunks_sanity(input):
    original, chunks = input
    joined = b''.join(chunks)
    assert_that(joined, equal_to(original))
