import ast
from pathlib import Path

from solution import total

SOLUTION = Path(__file__).with_name("solution.py")


def test_empty_list():
    assert total([]) == 0, "The empty list must give 0: that is the base case. Did you return None or forget it?"


def test_one_item():
    assert total([5]) == 5, "total([5]) is 5. Check that the base case is reached after one element."


def test_two_items():
    assert total([2, 3]) == 5, "total([2, 3]) is 5: first element plus the sum of the rest."


def test_example():
    assert total([3, 1, 4, 1, 5]) == 14, "total([3, 1, 4, 1, 5]) is 14. Is every element added exactly once?"


def test_negative_and_float():
    assert total([-2, 2.5]) == 0.5, "Negative numbers and floats are added like any other number."


def test_long_list():
    xs = list(range(900))
    assert total(xs) == 900 * 899 // 2, "900 items: 0 + 1 + ... + 899 = 404550. Is an element skipped or counted twice?"


def test_input_not_changed():
    xs = [1, 2, 3]
    total(xs)
    assert xs == [1, 2, 3], "total must not change the list (do not use pop or del to shrink it)."


def test_really_recursive():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    loops = [n for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While, ast.ListComp, ast.GeneratorExp))]
    assert not loops, "Solve it with recursion: no for/while loop and no comprehension in this problem."
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert "sum" not in names, "The built-in sum is not allowed here: write the recursion yourself."
    calls_itself = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == f.name
                       for f in ast.walk(tree) if isinstance(f, ast.FunctionDef)
                       for n in ast.walk(f))
    assert calls_itself, "total should call itself (or a helper that calls itself) on a smaller list."
