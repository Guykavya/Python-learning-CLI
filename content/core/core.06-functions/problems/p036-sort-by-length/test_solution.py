from solution import sort_by_length
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("solution.py").read_text()
TREE = ast.parse(SOURCE)


def called_names():
    """Names of every plain function called in your code, e.g. {'print', 'len'}."""
    return {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_example():
    assert sort_by_length(["banana", "Fig", "apple", "kiwi", "date"]) == ["Fig", "date", "kiwi", "apple", "banana"], (
        "Sort by length first; 'date' and 'kiwi' (both 4) alphabetically.")


def test_ignore_case():
    assert sort_by_length(["bb", "B", "a", "AA"]) == ["a", "B", "AA", "bb"], (
        "Ties are alphabetical IGNORING case: use w.lower() in the key.")


def test_empty_and_one():
    assert sort_by_length([]) == []
    assert sort_by_length(["x"]) == ["x"]


def test_input_unchanged():
    words = ["ccc", "a", "bb"]
    result = sort_by_length(words)
    assert words == ["ccc", "a", "bb"], "Use sorted(), which returns a new list; .sort() changes the caller's list."
    assert result == ["a", "bb", "ccc"]


def test_uses_lambda():
    assert any(isinstance(n, ast.Lambda) for n in ast.walk(TREE)), "Use a lambda as the key for this exercise."
