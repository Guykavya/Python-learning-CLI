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
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    # Pattern problem: use rstrip(), not strip(), so the first row keeps its leading spaces.
    return [line.rstrip() for line in r.stdout.rstrip().splitlines()]


import pytest


def diamond(n):
    top = [" " * (n - i) + "*" * (2 * i - 1) for i in range(1, n + 1)]
    return top + top[-2::-1] if n > 0 else []


def test_three():
    got = run("3\n")
    exp = ["  *", " ***", "*****", " ***", "  *"]
    assert got == exp, f"For n = 3:\nExpected: {exp}\nGot: {got}"


def test_one():
    got = run("1\n")
    assert got == ["*"], f"For n = 1 the diamond is a single star. Got {got}. Is the middle row printed twice?"


def test_zero():
    got = run("0\n")
    assert got == [], f"For n = 0 print nothing. Got {got}"


def test_middle_row_once():
    got = run("4\n")
    assert len(got) == 7, (
        f"For n = 4 expected 2*4 - 1 = 7 rows, got {len(got)}. "
        "If you got 8, the widest row is printed twice; start the bottom half at n - 1.")
    assert got.count("*******") == 1, f"The widest row must appear exactly once. Got {got}"


@pytest.mark.parametrize("n", [2, 5, 10, 30])
def test_sizes(n):
    got = run(f"{n}\n")
    exp = diamond(n)
    assert got == exp, (
        f"For n = {n}: row i (top half) has n - i spaces and 2*i - 1 stars; the bottom half mirrors it.\n"
        f"Expected: {exp}\nGot: {got}")


def test_no_trailing_spaces():
    r = subprocess.run([sys.executable, str(SOLUTION)], input="5\n",
                       capture_output=True, text=True, timeout=10)
    for line in r.stdout.splitlines():
        assert line == line.rstrip(), (
            f"The line {line!r} has spaces after the last star. Print only the leading spaces and the stars.")
