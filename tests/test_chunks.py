from hypothesis import given
from hypothesis.strategies import text
from hamcrest import assert_that, instance_of, equal_to

from .chunks import chunks

@given(text().flatmap(chunks))
def test_chunks_sanity(input):
    original, chunks = input
    joined = ''.join(chunks)
    assert_that(joined, equal_to(original))
