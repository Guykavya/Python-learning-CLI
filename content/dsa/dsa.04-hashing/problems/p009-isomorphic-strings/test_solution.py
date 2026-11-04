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


def brute(s, t):
    fwd = {}
    for a, b in zip(s, t):
        if fwd.setdefault(a, b) != b:
            return "NO"
    return "YES" if len(set(fwd.values())) == len(fwd) else "NO"


@pytest.mark.parametrize("s, t, expected, why", [
    ("egg", "add", "YES", "the example"),
    ("foo", "bar", "NO", "o would map to both a and r"),
    ("ab", "aa", "NO", "two different letters map to the same letter"),
    ("paper", "title", "YES", "p->t a->i e->l r->e"),
    ("badc", "baba", "NO", "b->b and d->b collide"),
    ("a", "z", "YES", "a single letter"),
    ("abc", "abc", "YES", "every letter maps to itself"),
    ("aa", "ab", "NO", "one letter maps to two different letters"),
])
def test_examples(s, t, expected, why):
    assert ask(s, t) == [expected], f"s={s!r}, t={t!r}: expected {expected} ({why}). Check BOTH directions."


def test_random_small():
    rng = random.Random(12)
    for _ in range(60):
        n = rng.randint(1, 7)
        s = "".join(rng.choice("abc") for _ in range(n))
        t = "".join(rng.choice("xyz") for _ in range(n))
        assert ask(s, t) == [brute(s, t)], f"s={s!r}, t={t!r}: expected {brute(s, t)}."


def test_large():
    rng = random.Random(13)
    s = "".join(rng.choice("abcdefghij") for _ in range(200000))
    table = dict(zip("abcdefghij", "klmnopqrst"))
    t = "".join(table[c] for c in s)
    assert ask(s, t) == ["YES"], "A consistent mapping on 200000 letters: YES, quickly."
    t2 = t[:-1] + ("k" if t[-1] != "k" else "l")
    assert ask(s, t2) == [brute(s, t2)], "One letter at the end breaks the mapping."
