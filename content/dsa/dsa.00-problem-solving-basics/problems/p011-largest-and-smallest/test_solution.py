import ast
import subprocess
import sys
from pathlib import Path

import pytest

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]


def called_names() -> set[str]:
    """Names of every plain function call in your solution, e.g. {'print', 'int', 'input'}."""
    tree = ast.parse(SOLUTION.read_text())
    return {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}



import ast

import pytest


def feed(numbers):
    return f"{len(numbers)}\n" + "".join(f"{x}\n" for x in numbers)


def check(numbers, why):
    expected = [f"max {max(numbers)}", f"min {min(numbers)}"]
    got = run(feed(numbers))
    assert got == expected, f"Numbers {numbers[:8]}: expected {expected}, got {got}. {why}"


def test_example():
    check([3, -1, 9, 2], "Compare every number with both the largest and the smallest so far.")


def test_all_negative():
    check([-5, -2, -8], "All numbers are negative. If max starts at 0, nothing beats it. Start from the first number.")


def test_all_positive():
    check([5, 2, 8], "All numbers are positive. If min starts at 0, nothing is smaller. Start from the first number.")


def test_single_number():
    check([42], "With one number it is both the max and the min.")


def test_single_negative():
    check([-7], "With one number it is both the max and the min, even if it is negative.")


def test_first_is_largest():
    check([100, 3, 50, -2, 7], "The first number is the largest. Make sure it is counted, not skipped.")


def test_last_is_smallest():
    check([4, 9, 6, 5, -30], "The last number is the smallest. Does your loop read and compare all n numbers?")


def test_all_equal():
    check([6, 6, 6], "All numbers are equal.")


def test_huge_values():
    check([10 ** 18, -(10 ** 18), 0, 123456789012345678],
          "Values reach 10^18. Do not use float(), which loses precision at this size.")


@pytest.mark.parametrize("seed", [1, 2])
def test_many(seed):
    numbers = [((i * 7919 + seed * 104729) % 20001) - 10000 for i in range(1000)]
    check(numbers, "1000 numbers in mixed order.")


def test_no_storing():
    tree = ast.parse(SOLUTION.read_text())
    calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    banned = calls & {"list", "sorted", "tuple", "set"}
    assert not banned, f"You used {sorted(banned)}. Do not store the numbers; keep only the largest and smallest so far."
    nodes = [n for n in ast.walk(tree) if isinstance(n, (ast.List, ast.ListComp, ast.Set, ast.SetComp))
             and not isinstance(getattr(n, "ctx", None), ast.Store)]
    assert not nodes, "Do not build a list (like [] or [x ...]). Keep only the largest and smallest so far."
