import pytest
from hypothesis import given, settings, strategies as st

from target import decode, encode

# Small alphabet so that runs, repeats and far-apart equal letters are common.
texts = st.text(alphabet="abc", max_size=30)
# Built from (letter, length) pieces so that long runs (more than 9) really appear.
runny = st.lists(st.tuples(st.sampled_from("xyz"), st.integers(1, 15)), max_size=5).map(
    lambda pieces: "".join(letter * n for letter, n in pieces))


@settings(derandomize=True, database=None, max_examples=100)
@given(texts)
def test_decode_undoes_encode(text):
    assert decode(encode(text)) == text, "decode(encode(t)) must give t back."


@settings(derandomize=True, database=None, max_examples=100)
@given(runny)
def test_round_trip_with_long_runs(text):
    assert decode(encode(text)) == text, "Runs longer than 9 need counts with several digits."


def test_known_encodings():
    assert encode("aaabcc") == "a3b1c2", "Every run is written with its count."
    assert encode("a" * 12) == "a12", "A run of 12 is one piece: a12."
    assert encode("") == "", "The empty text encodes to the empty text."


def test_digits_are_rejected():
    with pytest.raises(ValueError):
        encode("a1")
