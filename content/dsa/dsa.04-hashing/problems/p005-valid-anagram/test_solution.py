import subprocess
import sys
from pathlib import Path

import pytest

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import random


def ask(s, t, timeout=10):
    return run(f"{s}\n{t}\n", timeout=timeout)


@pytest.mark.parametrize("s, t, expected, why", [
    ("listen", "silent", "YES", "the example"),
    ("rat", "car", "NO", "t and c differ"),
    ("aab", "abb", "NO", "same letters, different counts"),
    ("a", "a", "YES", "single equal letters"),
    ("ab", "abc", "NO", "different lengths"),
    ("Ab", "ab", "NO", "case matters"),
    ("ad", "bc", "NO", "same sum of letter codes, but not anagrams"),
    ("aabbcc", "abcabc", "YES", "same counts in another order"),
])
def test_examples(s, t, expected, why):
    assert ask(s, t) == [expected], f"Inputs {s!r} and {t!r}: expected {expected} ({why})."


def test_random_small():
    rng = random.Random(7)
    for _ in range(40):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(1, 8)))
        t = list(s)
        rng.shuffle(t)
        if rng.random() < 0.5:
            t[rng.randrange(len(t))] = rng.choice("abcd")
        t = "".join(t)
        expected = "YES" if sorted(s) == sorted(t) else "NO"
        assert ask(s, t) == [expected], f"Inputs {s!r} and {t!r}: expected {expected}."


def test_large():
    rng = random.Random(8)
    s = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(200000))
    t = list(s)
    rng.shuffle(t)
    t = "".join(t)
    assert ask(s, t) == ["YES"], "200000 shuffled letters: this should be YES, and fast. Count, do not compare pairs."
    t2 = t[:-1] + ("a" if t[-1] != "a" else "b")
    assert ask(s, t2) == ["NO"], "One letter was changed, so the counts differ: NO."
