import ast
from pathlib import Path

import pytest

from solution import gcd

SOLUTION = Path(__file__).with_name("solution.py")


@pytest.mark.parametrize("a, b, want, why", [
    (12, 18, 6, "the example; the first step swaps the numbers"),
    (18, 12, 6, "the same pair in the other order"),
    (17, 5, 1, "coprime numbers have gcd 1"),
    (9, 0, 9, "gcd(a, 0) = a: this is the base case"),
    (0, 9, 9, "gcd(0, b) = b: the first step turns it into gcd(9, 0)"),
    (0, 0, 0, "gcd(0, 0) is defined as 0 here"),
    (7, 7, 7, "equal numbers"),
    (1, 10**18, 1, "1 divides everything"),
    (2**40, 2**30 * 3, 2**30, "large powers of two"),
])
def test_cases(a, b, want, why):
    assert gcd(a, b) == want, f"gcd({a}, {b}) should be {want}: {why}."


def test_many_steps():
    a, b = 1, 1
    while b < 10**18:
        a, b = b, a + b
    assert gcd(b, a) == 1, "Two neighbouring Fibonacci numbers: the slowest case for Euclid. Use % (not repeated subtraction)."


def test_large_values():
    assert gcd(10**18, 10**18 - 1) == 1, "Neighbouring numbers are coprime. Repeated subtraction would need 10**18 steps."
    assert gcd(123456789 * 10**9, 987654321 * 10**9) == 9 * 10**9, "gcd(123456789e9, 987654321e9) = 9e9."


def test_no_math_gcd():
    text = SOLUTION.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
            assert "math" not in mods, "math.gcd is not allowed: write Euclid's rule yourself."
