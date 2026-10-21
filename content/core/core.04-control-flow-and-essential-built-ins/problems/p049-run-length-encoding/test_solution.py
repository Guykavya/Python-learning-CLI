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


def rle(t):
    out, i = "", 0
    while i < len(t):
        j = i
        while j < len(t) and t[j] == t[i]:
            j += 1
        out += f"{t[i]}{j - i}"
        i = j
    return out


@pytest.mark.parametrize("text", ["aaabccdddd", "abc", "zzzzzzzzzzzz", "aabaa", "a", "ab  cd", "xxxxy", "yxxxx", "1112223"])
def test_encode(text):
    got = run(text + "\n")
    assert got == [rle(text)], (
        f"{text!r} should encode as {rle(text)!r}, got {got}. A run ends when the character changes, "
        "and the last run must be added after the loop.")


def test_last_run_written():
    assert run("aaab\n") == ["a3b1"], "The final run (b1) has no different character after it. Add it after the loop."


def test_empty():
    assert run("\n") == ["(empty)"], "An empty line has no runs. Do not index text[0] when text is empty."
