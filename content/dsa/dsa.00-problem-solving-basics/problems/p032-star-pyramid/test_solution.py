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


def pyramid(n):
    return [" " * (n - i) + "*" * (2 * i - 1) for i in range(1, n + 1)]


def test_four():
    got = run("4\n")
    assert got == ["   *", "  ***", " *****", "*******"], (
        f"For n = 4 expected 4 rows with 3, 2, 1, 0 leading spaces and 1, 3, 5, 7 stars, got {got}")


def test_one():
    got = run("1\n")
    assert got == ["*"], f"For n = 1 the pyramid is a single star with no spaces before it, got {got}"


def test_zero():
    got = run("0\n")
    assert got == [], f"For n = 0 print nothing at all, got {got}"


@pytest.mark.parametrize("n", [2, 3, 7, 40])
def test_sizes(n):
    got = run(f"{n}\n")
    expected = pyramid(n)
    assert len(got) == n, f"For n = {n} expected exactly {n} rows, got {len(got)} rows"
    assert got == expected, (
        f"For n = {n}, row i must have n - i spaces then 2*i - 1 stars.\nExpected: {expected}\nGot: {got}")


def test_no_trailing_spaces():
    r = subprocess.run([sys.executable, str(SOLUTION)], input="5\n",
                       capture_output=True, text=True, timeout=10)
    for line in r.stdout.splitlines():
        assert line == line.rstrip(), (
            f"The line {line!r} has spaces after the last star. Print only the leading spaces and the stars.")
