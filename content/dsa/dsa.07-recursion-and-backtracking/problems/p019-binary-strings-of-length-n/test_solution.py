import ast
from pathlib import Path

from solution import binary_strings

SOLUTION = Path(__file__).with_name("solution.py")


def test_zero():
    assert binary_strings(0) == [""], "n = 0: exactly one string, the empty one. Return [''], not []."


def test_one():
    assert binary_strings(1) == ["0", "1"], "n = 1: ['0', '1'] in this order."


def test_two_in_order():
    assert binary_strings(2) == ["00", "01", "10", "11"], "n = 2 in dictionary order. Try '0' before '1' at every level."


def test_three():
    want = ["000", "001", "010", "011", "100", "101", "110", "111"]
    got = binary_strings(3)
    assert sorted(got) == want, f"n = 3 should give the 8 strings {want}. Did you forget to pop?"
    assert got == want, "All strings are there, but not in dictionary order."


def test_strings_not_lists():
    got = binary_strings(2)
    assert all(isinstance(s, str) for s in got), "Each answer must be a string such as '01', not a list ['0', '1']. Use ''.join(path)."


def test_ten():
    got = binary_strings(10)
    assert len(got) == 1024, f"n = 10 has 2^10 = 1024 strings, got {len(got)}."
    assert got == sorted(got) and len(set(got)) == 1024, "The 1024 strings must be different and sorted."
    assert all(len(s) == 10 for s in got), "Every string must have length exactly 10."


def test_no_shortcuts():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
            assert "itertools" not in mods, "itertools is not allowed here: write the backtracking yourself."
        if isinstance(node, ast.Name):
            assert node.id not in ("format", "bin"), "format()/bin() are not allowed here: build the strings by backtracking."
