from solution import make_counter
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("solution.py").read_text()
TREE = ast.parse(SOURCE)


def called_names():
    """Names of every plain function called in your code, e.g. {'print', 'len'}."""
    return {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_counts_up():
    c = make_counter()
    assert [c(), c(), c()] == [1, 2, 3], "Each call adds 1 and returns the new count."


def test_start_and_step():
    d = make_counter(10, step=5)
    assert [d(), d()] == [15, 20]
    n = make_counter(step=-1)
    assert [n(), n()] == [-1, -2]


def test_independent():
    a = make_counter()
    b = make_counter()
    a(); a(); a()
    assert b() == 1, "Each counter needs its own count. Did you use a global?"
    assert a() == 4


def test_uses_nonlocal():
    assert any(isinstance(n, ast.Nonlocal) for n in ast.walk(TREE)), "Use nonlocal for the count."
