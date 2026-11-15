import random

import pytest

from solution import decode


@pytest.mark.parametrize("s, want, why", [
    ("3[a]2[bc]", "aaabcbc", "two groups side by side"),
    ("3[a2[c]]", "accaccacc", "a nested group: the inner 2[c] is cc"),
    ("2[abc]3[cd]ef", "abcabccdcdcdef", "plain letters after the groups"),
    ("10[x]", "x" * 10, "a two-digit count: build the number digit by digit"),
    ("ab", "ab", "no groups at all"),
    ("ab2[c]d", "abccd", "letters before a group must be kept: push the text built so far"),
    ("1[z]", "z", "a count of 1"),
    ("2[2[2[a]]]", "a" * 8, "three levels of nesting"),
    ("3[a]12[b]", "aaa" + "b" * 12, "the count of the second group must start from 0 again"),
    ("2[a3[b]c]", "abbbcabbbc", "letters on both sides of the inner group"),
    ("100[ab]", "ab" * 100, "a three-digit count"),
])
def test_cases(s, want, why):
    got = decode(s)
    assert got == want, f"decode({s!r}) should be {want!r}, got {got!r}: {why}."


def encode_random(rng, depth):
    parts_text, parts_plain = [], []
    for _ in range(rng.randint(1, 3)):
        if depth > 0 and rng.random() < 0.5:
            k = rng.randint(1, 12)
            t, p = encode_random(rng, depth - 1)
            parts_text.append(f"{k}[{t}]")
            parts_plain.append(p * k)
        else:
            w = "".join(rng.choice("abc") for _ in range(rng.randint(1, 3)))
            parts_text.append(w)
            parts_plain.append(w)
    return "".join(parts_text), "".join(parts_plain)


def test_random_round_trip():
    rng = random.Random(17)
    for _ in range(400):
        s, want = encode_random(rng, 3)
        got = decode(s)
        assert got == want, f"decode({s!r}) is wrong: expected {len(want)} characters starting {want[:30]!r}, got {got[:30]!r}."


def test_big_output():
    got = decode("1000[" + "10[ab]" + "]")
    assert len(got) == 20000 and got == "ab" * 10000, "1000[10[ab]] is 'ab' repeated 10,000 times."
