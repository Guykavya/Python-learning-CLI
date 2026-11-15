import random
import tracemalloc

import pytest

from solution import backspace_equal, type_text


def model(s):
    out = []
    for ch in s:
        if ch == "#":
            if out:
                out.pop()
        else:
            out.append(ch)
    return "".join(out)


@pytest.mark.parametrize("s, want, why", [
    ("ab#c", "ac", "# deletes the b"),
    ("a##c", "c", "the first # deletes a, the second has nothing left to delete"),
    ("#a#", "", "a backspace on an empty line does nothing"),
    ("", "", "empty"),
    ("abc", "abc", "no backspaces"),
    ("###", "", "only backspaces"),
    ("ab##cd#", "c", "ab deleted, then d deleted"),
])
def test_type_text(s, want, why):
    try:
        got = type_text(s)
    except IndexError:
        raise AssertionError(f"type_text({s!r}) crashed: only pop when the buffer is not empty.") from None
    assert got == want, f"type_text({s!r}) should be {want!r}, got {got!r}: {why}."


@pytest.mark.parametrize("a, b, want, why", [
    ("ab#c", "ad#c", True, "both type ac"),
    ("a#c", "b", False, "c is not b"),
    ("a##c", "#a#c", True, "both type c"),
    ("ab##", "c#d#", True, "both type the empty string"),
    ("a", "#", False, "one string keeps a letter, the other is empty"),
    ("#", "a", False, "the same, the other way round"),
    ("", "", True, "two empty strings"),
    ("bxj##tw", "bxo#j##tw", True, "both type btw"),
    ("y#fo##f", "y#f#o##f", True, "both type f"),
    ("abc#d", "abzz##d", True, "both type abd"),
    ("xywrrmp", "xywrrmu#p", True, "the backspace deletes the u"),
    ("a#b", "ab#", False, "b versus a"),
])
def test_backspace_equal(a, b, want, why):
    got = backspace_equal(a, b)
    assert got is want, f"backspace_equal({a!r}, {b!r}) should be {want}: {why}."


def test_random_against_model():
    rng = random.Random(19)
    for _ in range(2000):
        a = "".join(rng.choice("ab##") for _ in range(rng.randint(0, 8)))
        b = "".join(rng.choice("ab##") for _ in range(rng.randint(0, 8)))
        want = model(a) == model(b)
        assert backspace_equal(a, b) is want, f"backspace_equal({a!r}, {b!r}) should be {want}."
        assert type_text(a) == model(a), f"type_text({a!r}) should be {model(a)!r}."


def test_constant_memory():
    n = 10 ** 6
    a = "ab#" * (n // 3) + "z"
    b = "a" * (n // 3) + "z"
    tracemalloc.start()
    try:
        tracemalloc.reset_peak()
        got = backspace_equal(a, b)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert got is True, "Both big strings type 'a' repeated 333,333 times followed by 'z'."
    assert peak < 200_000, (
        f"backspace_equal allocated {peak:,} bytes for strings of 1,000,000 characters; O(1) extra memory means "
        "a few kilobytes at most. Do not build the typed texts or a list: walk both strings from the end with indices.")
