import ast
from pathlib import Path

import pytest

from solution import is_happy

SOLUTION = Path(__file__).with_name("solution.py")


def brute(n):
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(d) ** 2 for d in str(n))
    return n == 1


@pytest.mark.parametrize("n, want, why", [
    (19, True, "19 -> 82 -> 68 -> 100 -> 1"),
    (2, False, "2 -> 4 -> 16 -> 37 -> 58 -> 89 -> 145 -> 42 -> 20 -> 4: a loop without 1"),
    (1, True, "1 is happy at once (its next is 1 again)"),
    (7, True, "7 -> 49 -> 97 -> 130 -> 10 -> 1"),
    (4, False, "4 is inside the unhappy loop itself"),
    (10, True, "10 -> 1: a digit 0 adds nothing"),
    (100, True, "100 -> 1"),
    (2**31 - 1, False, "the largest input"),
])
def test_cases(n, want, why):
    got = is_happy(n)
    assert got is want, (
        f"is_happy({n}) should be {want} ({why}), got {got!r}. Return True only when the sequence reaches 1; "
        "a meeting of slow and fast elsewhere means a loop without 1.")


def test_first_thousand():
    for n in range(1, 1001):
        assert is_happy(n) is brute(n), f"is_happy({n}) should be {brute(n)}."


def test_no_set_of_seen_numbers():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    sets = [n for n in ast.walk(tree) if isinstance(n, (ast.Set, ast.SetComp, ast.Dict, ast.DictComp))]
    assert "set" not in names and "dict" not in names and not sets, (
        "Do not store the numbers you have seen: use slow and fast pointers on the sequence (O(1) memory).")
