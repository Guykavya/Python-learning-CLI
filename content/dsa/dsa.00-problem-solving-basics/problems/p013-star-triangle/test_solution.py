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
    # Pattern problem: rstrip() only, so any leading spaces on the first line are kept and checked.
    return [line.rstrip() for line in r.stdout.rstrip().splitlines()]


import pytest


def check(n):
    expected = ["*" * i for i in range(1, n + 1)]
    got = run(f"{n}\n")
    assert len(got) == n, (
        f"n = {n}: expected {n} rows, got {len(got)}. Use range(1, n + 1) so the rows have 1 to n stars, "
        "and do not print an empty first row.")
    for i, (e, g) in enumerate(zip(expected, got), start=1):
        assert g == e, (
            f"n = {n}: row {i} should be {e!r} ({i} stars, no spaces), got {g!r}. "
            "Leading spaces and spaces between stars count as wrong.")


@pytest.mark.parametrize("n", [1, 2, 4, 7])
def test_small(n):
    check(n)


def test_zero():
    got = run("0\n")
    assert got == [], f"n = 0: expected no output at all, got {got}."


def test_largest():
    check(50)
