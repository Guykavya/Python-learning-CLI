## Approach

Two round-trip tests with two different strategies, plus plain examples:

- `st.text(alphabet="abc", max_size=30)` has few letters, so the same letter appears in separate runs (`"aba"`) and the empty
  text shows up. That catches the encoder that counts letters globally, the one that drops the last run, and the decoder
  that crashes on `""`.
- The `runny` strategy builds texts from `(letter, length)` pieces with lengths up to 15, so runs with two-digit counts are common.
  That catches the decoder that reads one digit.
- `encode("a" * 12) == "a12"` is a **known answer**. The bug that writes `a9a3` still round-trips, because `decode` adds
  the pieces back together. Only a test of the encoded form can see it.
- `pytest.raises(ValueError)` for digits, because the codec is only defined for letters.

## Code

```python
import pytest
from hypothesis import given, settings, strategies as st

from target import decode, encode

texts = st.text(alphabet="abc", max_size=30)
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
```

## Cost

Three hundred generated inputs of at most 75 characters: well under a second.

## Another way

Also test the other direction, `encode(decode(code)) == code`, but only for codes that are valid (build them with a strategy that
produces `(letter, count)` pairs with different neighbouring letters). That one *would* have caught `a9a3`, because a canonical
code must come back unchanged. It needs a constructive strategy, which is the subject of p036.
