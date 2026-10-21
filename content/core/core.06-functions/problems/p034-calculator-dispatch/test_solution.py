import pytest
from solution import OPERATIONS, add, subtract, multiply, divide, calculate
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("solution.py").read_text()
TREE = ast.parse(SOURCE)


def called_names():
    """Names of every plain function called in your code, e.g. {'print', 'len'}."""
    return {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


@pytest.mark.parametrize("a, op, b, expected", [
    (6, "+", 3, 9), (6, "-", 3, 3), (6, "*", 3, 18), (6, "/", 3, 2.0), (-2, "*", 4, -8), (1, "/", 4, 0.25),
])
def test_calculate(a, op, b, expected):
    assert calculate(a, op, b) == expected


def test_divide_by_zero():
    assert calculate(6, "/", 0) is None, "divide must return None when b is 0."


def test_unknown_operator():
    assert calculate(6, "%", 3) is None, "Unknown operator: return None (use OPERATIONS.get, not [ ])."


def test_table_holds_functions():
    assert OPERATIONS == {"+": add, "-": subtract, "*": multiply, "/": divide}, (
        "OPERATIONS must map each symbol to the function object itself, e.g. '+': add (no parentheses).")
    assert OPERATIONS["*"](4, 5) == 20


def test_table_is_used():
    OPERATIONS["^"] = lambda a, b: a ** b
    try_result = calculate(2, "^", 5)
    del OPERATIONS["^"]
    assert try_result == 32, "calculate must look the operator up in OPERATIONS, so new entries work."


def test_no_if_chain_on_operator():
    symbols = {"+", "-", "*", "/"}
    for node in ast.walk(TREE):
        if isinstance(node, ast.Compare):
            for c in [node.left, *node.comparators]:
                assert not (isinstance(c, ast.Constant) and c.value in symbols), (
                    "Do not compare op with '+', '-', ... in an if-chain; look it up in OPERATIONS.")
