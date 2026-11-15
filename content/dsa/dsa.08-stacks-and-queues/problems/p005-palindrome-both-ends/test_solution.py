import random

import pytest

from solution import first_mismatch


@pytest.mark.parametrize("text, want, why", [
    ("A man, a plan, a canal: Panama", None, "the classic: ignore case, spaces and punctuation"),
    ("racecars", ("r", "s"), "the very first pair already differs"),
    ("abcxba", ("c", "x"), "the third pair from the outside differs"),
    ("", None, "the empty text is a palindrome"),
    ("x", None, "one character is a palindrome"),
    ("abba", None, "even length palindrome"),
    ("abcba", None, "odd length palindrome: the middle c is never compared"),
    ("ab", ("a", "b"), "two different characters"),
    ("Aa", None, "compare in lower case"),
    ("No 'x' in Nixon", None, "punctuation and spaces are skipped"),
    ("12321", None, "digits count"),
    ("1a2", ("1", "2"), "digits and letters are both kept"),
    ("!!!", None, "no letters or digits at all: nothing can differ"),
    ("Was it a car or a cat I saw?", None, "a longer palindrome"),
    ("Step on no pets!", None, "palindrome with odd length after cleaning"),
    ("abXcdcba", ("x", "c"), "the pair is reported in lower case, left character first"),
])
def test_cases(text, want, why):
    got = first_mismatch(text)
    assert got == want, f"first_mismatch({text!r}) should be {want!r}, got {got!r}: {why}."


def test_random_against_two_pointers():
    rng = random.Random(5)
    for _ in range(500):
        n = rng.randint(0, 9)
        half = [rng.choice("abAB1 ,") for _ in range(n)]
        text = "".join(half + half[::-1]) if rng.random() < 0.5 else "".join(half)
        s = [c.lower() for c in text if c.isalnum()]
        want = None
        i, j = 0, len(s) - 1
        while i < j:
            if s[i] != s[j]:
                want = (s[i], s[j])
                break
            i += 1
            j -= 1
        assert first_mismatch(text) == want, f"first_mismatch({text!r}) should be {want!r}."


def test_long_text():
    text = "ab" * 50000 + "c" + "ba" * 50000
    assert first_mismatch(text) is None, "A 200,001-character palindrome must return None."
    assert first_mismatch("z" + text) == ("z", "a"), "The first pair is ('z', 'a')."
