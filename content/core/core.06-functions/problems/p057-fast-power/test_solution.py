import sys
import pytest
import solution
from solution import power
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("solution.py").read_text()
TREE = ast.parse(SOURCE)


def called_names():
    """Names of every plain function called in your code, e.g. {'print', 'len'}."""
    return {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def function_node(name):
    return next(n for n in ast.walk(TREE) if isinstance(n, ast.FunctionDef) and n.name == name)


def calls_itself(name):
    """True if the function with this name contains a call to itself."""
    fn = function_node(name)
    return any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == name
               for c in ast.walk(fn))


def has_loop(name):
    return any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(function_node(name)))


@pytest.mark.parametrize("b, e", [(2, 10), (3, 5), (7, 0), (-2, 3), (1.5, 2), (10, 1), (0, 0), (0, 5), (5, 13)])
def test_values(b, e):
    assert power(b, e) == b ** e, f"power({b}, {e}) should be {b ** e}."


def test_huge_exponent():
    assert power(2, 100_000) == 2 ** 100_000, (
        "Large exponents must work. Recursing on exp - 1 hits the recursion limit; halve exp instead.")


def test_few_calls():
    count = 0
    original = solution.power

    def counting(b, e):
        nonlocal count
        count += 1
        return original(b, e)

    solution.power = counting
    try:
        original(3, 1000)
    finally:
        solution.power = original
    assert count <= 25, (
        f"power(3, 1000) made {count} recursive calls. Compute the half power ONCE and reuse it; "
        "about log2(1000) = 10 calls are enough.")


def test_rules():
    assert calls_itself("power"), "power must be recursive."
    assert not any(isinstance(n, ast.BinOp) and isinstance(n.op, ast.Pow) for n in ast.walk(TREE)), "Do not use **."
    assert "pow" not in called_names(), "Do not use pow()."
