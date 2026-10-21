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


def columns(m, w):
    return "".join(m[c::w] for c in range(w))


def test_example():
    assert run("WEAREDISCOVERED\n5\n") == ["WDVEIEASRRCEEOD"], (
        "Column c holds positions c, c + width, c + 2*width, ... Read all of column 0 first.")


def test_short_last_row():
    assert run("abcdefg\n3\n") == ["adgbecf"], (
        "Rows abc / def / g: the last row is short. Column 0 is a,d,g; column 1 is b,e; column 2 is c,f.")


@pytest.mark.parametrize("m, w", [("hi", 10), ("hello", 1), ("hello", 5), ("ab cd", 2), ("on the go", 3), ("x", 1), ("programming", 4)])
def test_more(m, w):
    got = run(f"{m}\n{w}\n")
    assert got == [columns(m, w)], (
        f"Message {m!r}, width {w}: expected {[columns(m, w)]}, got {got}. Spaces count as characters.")


@pytest.mark.parametrize("w", [0, -2])
def test_invalid_width(w):
    assert run(f"hello\n{w}\n") == ["invalid width"], "A width of 0 or less makes no sense (and range step 0 crashes)."
