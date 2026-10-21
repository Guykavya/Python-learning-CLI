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
    # rstrip(), not strip(): strip() would also remove the leading spaces of the first row.
    return [line.rstrip() for line in r.stdout.rstrip().splitlines()]

import pytest


def pyramid(n):
    """Independent check used only by the tests."""
    rows = []
    for i in range(1, n + 1):
        up = "".join(str(v % 10) for v in range(1, i + 1))
        down = "".join(str(v % 10) for v in range(i - 1, 0, -1))
        rows.append(" " * (n - i) + up + down)
    return rows


def compare(n):
    expected = pyramid(n)
    got = run(f"{n}\n")
    assert len(got) == n, f"n = {n}: expected {n} rows, got {len(got)}."
    for i, (e, g) in enumerate(zip(expected, got), start=1):
        assert g == e, (
            f"n = {n}, row {i}: expected {e!r}, got {g!r}. Row i has n - i spaces, then 1..i, "
            "then i-1..1, each written as value % 10, with no spaces between digits.")


def test_one_row():
    got = run("1\n")
    assert got == ["1"], f"n = 1: expected ['1'], got {got}. No leading space for the only row."


def test_three_rows():
    got = run("3\n")
    assert got == ["  1", " 121", "12321"], (
        f"n = 3: expected ['  1', ' 121', '12321'], got {got}. If the peak appears twice (e.g. 123321), "
        "the falling part should start at i - 1, not i.")


def test_ten_rows_has_zero_at_peak():
    compare(10)
    got = run("10\n")
    assert got[-1] == "1234567890987654321", (
        f"n = 10, last row: expected '1234567890987654321', got {got[-1]!r}. 10 is written as its last digit, 0.")


@pytest.mark.parametrize("n", [2, 5, 12, 30])
def test_other_sizes(n):
    compare(n)
