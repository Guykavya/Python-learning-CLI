import pytest
from solution import evaluate, to_text
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


E = ("+", 2, ("*", 3, 4))


def test_example():
    assert evaluate(E) == 14
    assert to_text(E) == "(2 + (3 * 4))"


def test_numbers():
    assert evaluate(42) == 42 and evaluate(2.5) == 2.5
    assert to_text(42) == "42" and to_text(-3) == "-3"


def test_neg():
    assert evaluate(("neg", ("-", 1, 5))) == 4
    assert to_text(("neg", ("-", 1, 5))) == "-(1 - 5)"
    assert evaluate(("neg", ("neg", 3))) == 3


def test_division_and_deep():
    assert evaluate(("/", 7, 2)) == 3.5
    deep = ("-", ("*", ("+", 1, 2), ("/", 9, 3)), ("neg", 4))
    assert evaluate(deep) == 13.0, "Evaluate both sides recursively, whatever their depth."
    assert to_text(deep) == "(((1 + 2) * (9 / 3)) - -4)"


def test_left_heavy_chain():
    expr = 0
    for i in range(1, 101):
        expr = ("+", expr, i)
    assert evaluate(expr) == 5050


def test_recursive():
    assert calls_itself("evaluate") and calls_itself("to_text")


def test_dispatch_not_if_chain():
    for node in ast.walk(TREE):
        if isinstance(node, ast.Compare):
            for c in [node.left, *node.comparators]:
                assert not (isinstance(c, ast.Constant) and c.value in {"+", "-", "*", "/"}), (
                    "Look binary operators up in a dict of functions instead of comparing op with '+', '-', ...")
