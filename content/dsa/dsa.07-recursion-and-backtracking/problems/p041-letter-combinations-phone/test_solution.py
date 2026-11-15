import ast
from pathlib import Path

import pytest

from solution import letter_combinations

SOLUTION = Path(__file__).with_name("solution.py")
PHONE = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}


def expected(digits):
    if not digits:
        return []
    out = [""]
    for d in digits:
        out = [s + ch for s in out for ch in PHONE[d]]
    return sorted(out)


def test_example():
    got = sorted(letter_combinations("23"))
    assert got == ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"], f"'23' gives 9 strings, got {got}."


def test_empty():
    assert letter_combinations("") == [], "The empty digit string gives [] in this problem (not [''])."


@pytest.mark.parametrize("digits", ["2", "7", "9", "79", "234", "2345", "777", "596"])
def test_against_expected(digits):
    got = letter_combinations(digits)
    want = expected(digits)
    assert all(isinstance(s, str) for s in got), "Each answer must be a string such as 'ad'."
    assert sorted(got) == want, (
        f"letter_combinations({digits!r}) should give {len(want)} strings, got {len(got)}. "
        "Remember that 7 is 'pqrs' and 9 is 'wxyz' (four letters).")


def test_six_digits():
    got = letter_combinations("234567")
    assert len(got) == 3 * 3 * 3 * 3 * 3 * 4 and len(set(got)) == len(got), "'234567' has 3^5 * 4 = 972 different strings."


def test_no_itertools():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
            assert "itertools" not in mods, "itertools is not allowed here: write the backtracking yourself."
