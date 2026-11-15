import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import remove_duplicates

HERE = Path(__file__).parent


def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def slow(s):
    pairs = 0
    changed = True
    while changed:
        changed = False
        for i in range(len(s) - 1):
            if s[i] == s[i + 1]:
                s = s[:i] + s[i + 2:]
                pairs += 1
                changed = True
                break
    return (s, pairs)


@pytest.mark.parametrize("s, want, why", [
    ("abbaca", ("ca", 2), "bb goes, then aa becomes neighbours and goes too"),
    ("azxxzy", ("ay", 2), "xx goes, then zz"),
    ("aabb", ("", 2), "everything cancels: the result is the empty string"),
    ("aaa", ("a", 1), "only PAIRS cancel: one a stays"),
    ("", ("", 0), "empty input"),
    ("a", ("a", 0), "a single character"),
    ("abc", ("abc", 0), "no neighbours are equal"),
    ("abccba", ("", 3), "a chain reaction: compare with the stack top, not with the previous input character"),
    ("aaaa", ("", 2), "two pairs"),
])
def test_cases(s, want, why):
    got = remove_duplicates(s)
    assert got == want, f"remove_duplicates({s!r}) should be {want}, got {got}: {why}."


def test_random_against_slow():
    rng = random.Random(18)
    for _ in range(500):
        s = "".join(rng.choice("ab" if rng.random() < 0.5 else "abc") for _ in range(rng.randint(0, 12)))
        assert remove_duplicates(s) == slow(s), f"remove_duplicates({s!r}) should be {slow(s)}."


def test_long_in_time():
    code = (
        "from solution import remove_duplicates\n"
        "s = ''.join(chr(97 + i % 26) for i in range(50000))\n"
        "r, p = remove_duplicates(s + s[::-1])\n"
        "print(repr(r), p)\n"
    )
    out = run_code(code, 20, "A 100,000-character string that cancels completely (one pass with a stack, not repeated replace)")
    assert out == "'' 50000", f"The big string cancels completely in 50,000 pairs; you printed {out}."
