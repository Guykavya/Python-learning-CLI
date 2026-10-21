from solution import apply_to_all
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("solution.py").read_text()
TREE = ast.parse(SOURCE)


def called_names():
    """Names of every plain function called in your code, e.g. {'print', 'len'}."""
    return {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_len():
    assert apply_to_all(len, ["a", "bcd", ""]) == [1, 3, 0]


def test_method_and_lambda():
    assert apply_to_all(str.title, ["asha", "ravi"]) == ["Asha", "Ravi"]
    assert apply_to_all(lambda n: n * n, [1, 2, 3]) == [1, 4, 9]


def test_empty():
    assert apply_to_all(abs, []) == []


def test_input_unchanged():
    data = [-1, -2]
    result = apply_to_all(abs, data)
    assert data == [-1, -2], "Build a new list; do not replace the items of the caller's list."
    assert result == [1, 2] and result is not data


def test_returns_list():
    assert isinstance(apply_to_all(str, [1]), list), "Return a list, not a map object."


def test_no_map():
    assert "map" not in called_names(), "Write the loop yourself instead of calling map()."
