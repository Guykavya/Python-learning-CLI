import ast
from pathlib import Path

from solution import clean_scores

TREE = ast.parse(Path(__file__).with_name("solution.py").read_text())


def test_example():
    got = clean_scores(["88", " 7", "abc", "+3", "-5", "²", "100", "4.0", "", "1_0"])
    assert got == ([88, 7, 3, 100, 10], ["abc", "-5", "²", "4.0", ""]), f"Got {got}."


def test_spaces_and_signs_are_numbers():
    scores, rejected = clean_scores([" 7", "+3", "\t42\n"])
    assert scores == [7, 3, 42], (
        "int() accepts surrounding whitespace and a + sign. If these were rejected, you checked "
        "with isdigit() instead of letting int() decide.")


def test_superscript_is_rejected_not_crash():
    scores, rejected = clean_scores(["²", "5"])
    assert rejected == ["²"] and scores == [5], (
        "'²'.isdigit() is True but int('²') raises ValueError. Use try/except ValueError around int().")


def test_range():
    scores, rejected = clean_scores(["0", "100", "101", "-1", "-0"])
    assert scores == [0, 100, 0], "0 and 100 are allowed; '-0' is int 0, also allowed."
    assert rejected == ["101", "-1"], "Out-of-range values are rejected, keeping the original token."


def test_rejected_unchanged():
    _, rejected = clean_scores(["  abc  "])
    assert rejected == ["  abc  "], "Put the original token in rejected, not a stripped copy."


def test_no_isdigit_family():
    methods = {n.func.attr for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    banned = methods & {"isdigit", "isnumeric", "isdecimal"}
    assert not banned, f"Do not use {sorted(banned)}: let int() be the check (EAFP)."
