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
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import pytest


def zeros(n):
    """Independent check used only by the tests."""
    count = 0
    while n > 0:
        n //= 5
        count += n
    return count


@pytest.mark.parametrize("n, expected", [
    (0, 0), (1, 0), (4, 0), (5, 1), (9, 1), (10, 2), (24, 4),
])
def test_small(n, expected):
    got = run(f"{n}\n")
    assert got == [str(expected)], f"n = {n}: expected {expected}, got {got}."


def test_25_has_an_extra_five():
    got = run("25\n")
    assert got == ["6"], (
        f"n = 25: expected 6, got {got}. 25 = 5 * 5 gives TWO factors of 5. Counting only n // 5 gives 5; "
        "you also need n // 25, n // 125, ...")


@pytest.mark.parametrize("n, expected", [(100, 24), (124, 28), (125, 31), (1000, 249)])
def test_powers_of_five(n, expected):
    got = run(f"{n}\n")
    assert got == [str(expected)], (
        f"n = {n}: expected {expected}, got {got}. 125 = 5 * 5 * 5 contributes three 5s. "
        "Keep dividing by higher powers of 5 until the power is larger than n.")


def test_huge_n_fast():
    n = 10 ** 18
    got = run(f"{n}\n", timeout=3)
    assert got == [str(zeros(n))], (
        f"n = 10^18: expected {zeros(n)}, got {got}. Do not compute n!; count factors of 5 with //.")


def test_huge_odd_value():
    n = 987654321987654321
    got = run(f"{n}\n", timeout=3)
    assert got == [str(zeros(n))], f"n = {n}: expected {zeros(n)}, got {got}."
