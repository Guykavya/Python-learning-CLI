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


def wrap(w, text):
    lines, cur = [], ""
    for word in text.split():
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= w:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines + [f"Lines: {len(lines)}"]


def test_example():
    assert run("12\nthe quick brown fox jumps over the lazy dog\n") == [
        "the quick", "brown fox", "jumps over", "the lazy dog", "Lines: 4"], (
        "'the lazy dog' is exactly 12 characters and fits. Did you print the last line after the loop?")


@pytest.mark.parametrize("w, text", [
    (5, "aaaaa bbbbb"),
    (11, "aaaaa bbbbb"),
    (10, "aaaaa bbbbb"),
    (3, "extraordinary is a long word"),
    (1, "a b c"),
    (80, "short text fits on one line"),
    (6, "   lots    of   spaces   here  "),
])
def test_wraps(w, text):
    got = run(f"{w}\n{text}\n")
    assert got == wrap(w, text), (
        f"Width {w}, text {text!r}: expected {wrap(w, text)}, got {got}. Count the space between words; "
        "a too-long word gets its own line.")


def test_no_lines_exceed_width_except_long_words():
    got = run("7\nab cd ef gh ij kl\n")
    assert got == ["ab cd", "ef gh", "ij kl", "Lines: 3"], (
        "'ab cd ef' would be 8 characters, which is more than 7. Include the space in your length check.")


def test_empty():
    assert run("10\n\n") == ["Lines: 0"], "No words: no lines, and no empty line printed."
