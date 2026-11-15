import ast
from pathlib import Path

from solution import reverse

SOLUTION = Path(__file__).with_name("solution.py")


def test_empty():
    assert reverse("") == "", "The empty string reversed is the empty string: that is a good base case."


def test_one_char():
    assert reverse("x") == "x", "One character reversed is itself."


def test_example():
    assert reverse("abc") == "cba", "reverse('abc') is 'cba'. If you got 'abc', the first character is put in front instead of at the end."


def test_palindrome():
    assert reverse("racecar") == "racecar", "A palindrome reads the same backwards."


def test_even_length():
    assert reverse("abcd") == "dcba", "Even length: 'abcd' -> 'dcba'. Check that no character is lost in the middle."


def test_unicode_and_spaces():
    assert reverse("naïve café") == "éfac evïan", "Spaces and letters like 'ï' and 'é' are ordinary characters."


def test_long():
    s = "ab" * 250
    assert reverse(s) == "ba" * 250, "A 500-character string. Is your recursion depth more than about 500?"


def test_no_shortcuts():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        assert not isinstance(node, (ast.For, ast.While, ast.ListComp, ast.GeneratorExp)), \
            "Solve it with recursion: no loops or comprehensions here."
        if isinstance(node, ast.Name):
            assert node.id != "reversed", "reversed() is not allowed: write the recursion yourself."
        if isinstance(node, ast.Slice) and node.step is not None:
            assert False, "A slice with a step (like s[::-1]) is not allowed here."
