import ast
from pathlib import Path

import pytest

from solution import reverse_string

SOLUTION = Path(__file__).with_name("solution.py")


@pytest.mark.parametrize("s, want, why", [
    ("", "", "the empty string reversed is still empty: do not pop from an empty stack"),
    ("a", "a", "one character reversed is itself"),
    ("ab", "ba", "two characters swap places"),
    ("stack", "kcats", "the example"),
    ("racecar", "racecar", "a palindrome reads the same both ways"),
    ("hello world", "dlrow olleh", "spaces are characters too"),
    ("naïve ☕😀", "😀☕ evïan", "accented letters and emoji are single characters in Python"),
])
def test_cases(s, want, why):
    got = reverse_string(s)
    assert got == want, (f"reverse_string({s!r}) should be {want!r}, got {got!r}: {why}. "
                         "If the string came back unchanged, you probably popped from the front with pop(0).")


def test_long_string():
    s = "".join(chr(97 + i % 26) for i in range(10 ** 5))
    assert reverse_string(s) == s[::-1], "A string of 100,000 characters must be reversed completely."


def test_uses_a_stack():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    slices = [n for n in ast.walk(tree) if isinstance(n, ast.Slice) and n.step is not None]
    assert "reversed" not in names and "reverse" not in attrs and not slices, (
        "Do not use reversed(), .reverse() or a [::-1] slice here: push the characters and pop them back.")
    assert "append" in attrs and "pop" in attrs, "Use a list as a stack: append (push) and pop."
