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

import os
import pytest


def lcp(words):
    p = os.path.commonprefix(words)
    return [f"Prefix: {p or '(none)'}", f"Length: {len(p)}"]


@pytest.mark.parametrize("line", [
    "flower flow flight", "interview internet interval", "dog car", "same same", "solo",
    "abc abcd ab", "ab abc abcd", "prefix prefixes pre", "Apple apple", "a a a a", "xyz xya xab",
])
def test_prefix(line):
    words = line.split()
    got = run(line + "\n")
    assert got == lcp(words), (
        f"For {line!r} expected {lcp(words)}, got {got}. Walk the shortest word and stop at the first "
        "position where some word differs. Comparison is case-sensitive.")


def test_short_word_last_does_not_crash():
    assert run("abcdef abcxyz ab\n") == ["Prefix: ab", "Length: 2"], (
        "The shortest word is last. Indexing beyond a short word's end crashes; walk the shortest word.")


def test_no_words():
    assert run("  \n") == ["No words"], "No words: print only No words."
