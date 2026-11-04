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


def ask(note, magazine, timeout=10):
    return run(f"{note}\n{magazine}\n", timeout=timeout)


@pytest.mark.parametrize("note, magazine, expected, why", [
    ("aab", "baa", "YES", "the example"),
    ("aab", "ba", "NO", "only one a in the magazine; a set check would say YES"),
    ("a", "b", "NO", "letter missing completely"),
    ("a", "a", "YES", "one letter each"),
    ("abc", "aabbccdd", "YES", "extra magazine letters are fine"),
    ("aaa", "aa", "NO", "short by one"),
    ("zz", "zaz", "YES", "letters do not need to be adjacent"),
])
def test_examples(note, magazine, expected, why):
    assert ask(note, magazine) == [expected], f"Note {note!r}, magazine {magazine!r}: expected {expected} ({why})."


def test_random_small():
    rng = random.Random(10)
    for _ in range(40):
        note = "".join(rng.choice("abc") for _ in range(rng.randint(1, 8)))
        mag = "".join(rng.choice("abc") for _ in range(rng.randint(1, 12)))
        ok = all(note.count(c) <= mag.count(c) for c in set(note))
        assert ask(note, mag) == ["YES" if ok else "NO"], f"Note {note!r}, magazine {mag!r}: expected {'YES' if ok else 'NO'}."


def test_large():
    rng = random.Random(11)
    mag = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(200000))
    note = mag[:150000]
    assert ask(note, mag) == ["YES"], "The note is a piece of the magazine: YES, and quickly."
    assert ask(note + "a" * 20000, mag) == ["NO"], "Too many a's were asked for: NO."
