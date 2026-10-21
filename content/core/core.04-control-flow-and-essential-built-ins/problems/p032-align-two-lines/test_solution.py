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

import subprocess
import sys
import pytest


def raw(stdin):
    r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin, capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return r.stdout.splitlines()


def align(t, b):
    l1, l2 = [], []
    for x, y in zip(t.split(), b.split()):
        w = max(len(x), len(y))
        l1.append(f"{x:>{w}}" if x.isdigit() else f"{x:<{w}}")
        l2.append(f"{y:>{w}}" if y.isdigit() else f"{y:<{w}}")
    return ["  ".join(l1).rstrip(), "  ".join(l2).rstrip()]


def test_example():
    assert raw("item qty price\nnotebook 3 45\n") == ["item      qty  price", "notebook    3     45"], (
        "Each column is as wide as its longer word. Digit-only words are right-aligned. "
        "Two spaces between columns.")


@pytest.mark.parametrize("t, b", [
    ("1 22 333", "4444 55 6"),
    ("name age", "Bhavya 19"),
    ("x", "y"),
    ("100 apples", "pears 7"),
    ("a1 b2", "33 c"),
    ("total", "1234567"),
])
def test_alignment(t, b):
    got = raw(f"{t}\n{b}\n")
    want = align(t, b)
    assert got == want, (
        f"For {t!r} / {b!r} expected {want}, got {got}. Decide the alignment per word "
        "(isdigit), and use max(len(top), len(bottom)) as the column width.")


def test_no_trailing_spaces():
    for line in raw("abc 1\nx 12345\n"):
        assert line == line.rstrip(), f"Line {line!r} ends with spaces. Use rstrip() before printing."


def test_mismatch():
    assert raw("a b c\nd e\n") == ["Lines have different word counts"], (
        "Different word counts: print only the message. Check before zip, which drops extra words silently.")
