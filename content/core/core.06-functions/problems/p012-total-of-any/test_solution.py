from solution import total
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("solution.py").read_text()
TREE = ast.parse(SOURCE)


def called_names():
    """Names of every plain function called in your code, e.g. {'print', 'len'}."""
    return {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_three():
    assert total(1, 2, 3) == 6, "total(1, 2, 3) should be 6. Is the parameter written *numbers?"


def test_one():
    assert total(10) == 10


def test_none():
    assert total() == 0, "With no arguments numbers is (), and the total is 0. Start your total at 0."


def test_floats_and_negatives():
    assert total(1.5, -0.5) == 1.0
    assert total(-1, -2, -3) == -6


def test_spread_list():
    values = [4, 5, 6]
    assert total(*values) == 15, "total(*values) passes 4, 5, 6 as three arguments."


def test_many():
    assert total(*range(1001)) == 500500


def test_no_sum_builtin():
    used = {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "sum" not in used, "Write the loop yourself for this exercise instead of calling sum()."
