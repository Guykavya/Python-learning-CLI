from solution import min_and_max
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("solution.py").read_text()
TREE = ast.parse(SOURCE)


def called_names():
    """Names of every plain function called in your code, e.g. {'print', 'len'}."""
    return {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_example():
    assert min_and_max([4, 9, 1, 7]) == (1, 9), "Expected the tuple (1, 9): smallest first, then largest."


def test_returns_tuple():
    assert isinstance(min_and_max([3, 1]), tuple), "Return a tuple: `return smallest, largest`."


def test_one_item():
    assert min_and_max([5]) == (5, 5), "With one item, it is both the smallest and the largest."


def test_all_negative():
    assert min_and_max([-2, -8]) == (-8, -2), (
        "Got the wrong answer for negatives. Did you start smallest/largest at 0? Start at numbers[0].")


def test_all_large():
    assert min_and_max([50, 70, 60]) == (50, 70), "Did you start smallest at 0? 0 is not in the list."


def test_empty():
    assert min_and_max([]) == (None, None), "An empty list has no smallest or largest: return (None, None)."


def test_list_unchanged():
    data = [3, 1, 2]
    min_and_max(data)
    assert data == [3, 1, 2], "Do not sort or change the caller's list."


def test_no_min_max_builtins():
    used = {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert not ({"min", "max", "sorted"} & used), (
        "Walk the list yourself; do not call min, max or sorted for this exercise.")
