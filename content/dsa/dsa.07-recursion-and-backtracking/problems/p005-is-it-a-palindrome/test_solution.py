import ast
from pathlib import Path

import pytest

from solution import is_palindrome

SOLUTION = Path(__file__).with_name("solution.py")


@pytest.mark.parametrize("s, want, why", [
    ("", True, "the empty string is a palindrome (base case)"),
    ("a", True, "one character is a palindrome (base case)"),
    ("level", True, "odd length: the middle character is compared with nothing"),
    ("abba", True, "even length: the two indexes cross without meeting"),
    ("ab", False, "two different characters"),
    ("abca", False, "the ends match but the inside 'bc' does not"),
    ("abcba", True, "a five-letter palindrome"),
    ("abcda", False, "the mismatch is in the middle pair"),
    ("Aa", False, "upper and lower case are different characters here"),
    ("a b a", True, "spaces count like other characters"),
    ("a ba", False, "spaces are not removed in this problem"),
])
def test_cases(s, want, why):
    assert is_palindrome(s) is want, f"is_palindrome({s!r}) should be {want}: {why}."


def test_long_palindrome():
    s = "ab" * 400 + "c" + "ba" * 400
    assert is_palindrome(s) is True, "A 1601-character palindrome. Recursing on both ends keeps the depth at about 800."


def test_long_not_palindrome():
    s = "ab" * 400 + "cd" + "ba" * 400
    assert is_palindrome(s) is False, "A long string with one mismatch in the very middle."


def test_no_shortcuts():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        assert not isinstance(node, (ast.For, ast.While, ast.ListComp, ast.GeneratorExp)), \
            "Use recursion on the two ends: no loops here."
        if isinstance(node, ast.Name):
            assert node.id != "reversed", "reversed() is not allowed in this problem."
        if isinstance(node, ast.Slice) and node.step is not None:
            assert False, "s[::-1] is not allowed here: compare the ends recursively."
