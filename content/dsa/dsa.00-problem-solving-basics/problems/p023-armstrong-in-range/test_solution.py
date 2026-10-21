import ast
import subprocess
import sys
from pathlib import Path

import pytest

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


def called_names() -> set[str]:
    """Names of every plain function call in your solution, e.g. {'print', 'int', 'input'}."""
    tree = ast.parse(SOLUTION.read_text())
    return {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def armstrongs(lo: int, hi: int) -> list[str]:
    out = []
    for x in range(lo, hi + 1):
        k = len(str(x))
        if sum(int(c) ** k for c in str(x)) == x:
            out.append(str(x))
    return out or ["none"]


def test_three_digit():
    got = run("100\n500\n")
    assert got == ["153", "370", "371", "407"], (
        f"Between 100 and 500 expected 153, 370, 371, 407; got {got}. Raise each digit to the power 3 here.")


def test_single_digits():
    got = run("0\n9\n")
    assert got == [str(d) for d in range(10)], (
        f"0 to 9 are all Armstrong numbers (d to the power 1 is d). Got {got}. Treat 0 as one digit.")


def test_zero_alone():
    got = run("0\n0\n")
    assert got == ["0"], f"0 is an Armstrong number. Got {got}."


def test_partial_single_digits():
    got = run("8\n12\n")
    assert got == ["8", "9"], f"Only 8 and 9 lie in 8..12. Got {got}. 10, 11, 12 are not Armstrong."


def test_none():
    got = run("10\n100\n")
    assert got == ["none"], (
        f"There is no Armstrong number from 10 to 100, so print exactly one line 'none'. Got {got}.")


def test_ends_included():
    assert run("153\n153\n") == ["153"], "When lo = hi = 153, print 153: both ends are included."
    assert run("154\n370\n") == ["370"], "370 is the upper end and must be included."


def test_four_digit():
    got = run("1000\n9999\n")
    assert got == ["1634", "8208", "9474"], (
        f"Four-digit Armstrong numbers use the power 4. Expected 1634, 8208, 9474; got {got}.")


def test_full_range():
    got = run("0\n100000\n", timeout=10)
    expected = armstrongs(0, 100000)
    assert got == expected, f"For 0..100000 expected {expected}, got {got}."


def test_no_strings():
    names = called_names()
    assert not names & {"str", "repr", "list", "map", "format"}, (
        "Do not convert the number to text. Use % 10 to get the last digit and // 10 to drop it.")
