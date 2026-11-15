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


def ask(pattern, sentence, timeout=10):
    return run(f"{pattern}\n{sentence}\n", timeout=timeout)


@pytest.mark.parametrize("pattern, sentence, expected, why", [
    ("abba", "dog cat cat dog", "YES", "the example"),
    ("abba", "dog cat cat fish", "NO", "a would be dog and fish"),
    ("abba", "dog dog dog dog", "NO", "a and b would both be dog"),
    ("aaaa", "dog cat cat dog", "NO", "one letter, several words"),
    ("a", "dog", "YES", "one letter, one word"),
    ("ab", "dog cat fish", "NO", "the lengths differ (zip would hide this)"),
    ("abc", "x y z", "YES", "all different, all mapped"),
    ("aba", "x x x", "NO", "a and b both mean x"),
])
def test_examples(pattern, sentence, expected, why):
    assert ask(pattern, sentence) == [expected], f"Pattern {pattern!r}, words {sentence!r}: expected {expected} ({why})."


def test_large():
    rng = random.Random(14)
    pattern = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(100000))
    words = " ".join("w" + c * 3 for c in pattern)
    assert ask(pattern, words) == ["YES"], "A consistent pattern with 100000 words: YES."
    broken = words[:-1] + ("z" if words[-1] != "z" else "y")
    assert ask(pattern, broken) == ["NO"], "The last word was changed, so a letter has two words: NO."
