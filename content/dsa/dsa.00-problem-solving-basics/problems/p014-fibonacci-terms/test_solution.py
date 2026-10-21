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



import pytest


def fib_line(n):
    terms = []
    a, b = 0, 1
    for _ in range(n):
        terms.append(str(a))
        a, b = b, a + b
    return " ".join(terms)


@pytest.mark.parametrize("n", [3, 7, 10, 20])
def test_small(n):
    expected = fib_line(n)
    got = run(f"{n}\n")
    assert got == [expected], (
        f"n = {n}: expected one line {expected!r}, got {got}. Print all terms on one line with "
        "single spaces. Update both terms at once with a, b = b, a + b.")


def test_zero():
    got = run("0\n")
    assert got == [], f"n = 0: expected no output at all, got {got}."


def test_one():
    got = run("1\n")
    assert got == ["0"], f"n = 1: expected just '0', got {got}. Do not print the first two terms before the loop."


def test_two():
    got = run("2\n")
    assert got == ["0 1"], f"n = 2: expected '0 1', got {got}."


def test_ninety():
    got = run("90\n")
    assert len(got) == 1, f"n = 90: expected a single line, got {len(got)} lines."
    terms = got[0].split()
    assert len(terms) == 90, f"n = 90: expected 90 terms, got {len(terms)}."
    assert terms[-1] == "1779979416004714189", (
        f"n = 90: the last term should be 1779979416004714189, got {terms[-1]}. Keep the numbers as ints, no float.")
    assert got[0] == fib_line(90), "n = 90: some term is wrong, or the spacing between terms is not a single space."
