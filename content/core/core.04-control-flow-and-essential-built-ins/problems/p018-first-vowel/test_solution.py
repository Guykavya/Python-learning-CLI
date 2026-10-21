import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or an input() call waiting for a line that never comes.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import pytest


@pytest.mark.parametrize("word, expected", [
    ("strength", "First vowel 'e' at position 3"),
    ("Apple", "First vowel 'A' at position 0"),
    ("queue", "First vowel 'u' at position 1"),
    ("bcdfgO", "First vowel 'O' at position 5"),
    ("tryst", "No vowels"),
    ("rhythm", "No vowels"),
])
def test_words(word, expected):
    got = run(word + "\n")
    assert got == [expected], (
        f"For {word!r} expected [{expected!r}], got {got}. Report only the first vowel, count positions from 0, "
        "and check capital vowels too.")


def test_empty_word():
    assert run("\n") == ["No vowels"], "An empty word has no vowels. Your loop runs zero times; what prints then?"
