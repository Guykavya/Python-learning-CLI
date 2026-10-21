import pytest
from solution import reverse, is_palindrome
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


@pytest.mark.parametrize("text", ["hello", "", "a", "ab", "Python 3!", "racecar"])
def test_reverse(text):
    assert reverse(text) == text[::-1], f"reverse({text!r}) should be {text[::-1]!r}."


@pytest.mark.parametrize("text, expected", [
    ("Racecar", True), ("A man, a plan, a canal: Panama!", True), ("hello", False), ("", True),
    ("a", True), ("ab", False), ("No 'x' in Nixon", True), ("12321", True), ("123", False), ("!!", True),
])
def test_palindrome(text, expected):
    assert is_palindrome(text) is expected, (
        f"is_palindrome({text!r}) should be {expected}. Lowercase, keep only letters and digits, then compare ends.")


def test_reverse_rules():
    assert calls_itself("reverse"), "reverse must call itself."
    assert not has_loop("reverse"), "No loops in reverse."
    fn = function_node("reverse")
    for node in ast.walk(fn):
        if isinstance(node, ast.Slice):
            assert node.step is None, "Do not use a step slice such as [::-1]."
    assert "reversed" not in called_names(), "Do not use reversed()."


def test_palindrome_recursive():
    recursive = [n.name for n in TREE.body if isinstance(n, ast.FunctionDef)
                 and n.name != "reverse" and calls_itself(n.name)]
    assert recursive, "is_palindrome (or a helper it calls) must be recursive."
