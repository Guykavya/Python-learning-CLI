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


def ask(*nums: int) -> list[str]:
    text = f"{len(nums)}\n" + "".join(f"{x}\n" for x in nums)
    return run(text)


def expected_for(nums) -> str:
    distinct = sorted(set(nums))
    return str(distinct[-2]) if len(distinct) >= 2 else "none"


def test_simple():
    got = ask(4, 9, 2, 7)
    assert got == ["7"], f"For 4 9 2 7 the largest is 9 and the next is 7. Got {got}."


def test_duplicate_max():
    got = ask(5, 5, 3)
    assert got == ["3"], (
        f"For 5 5 3 expected 3, got {got}. A repeat of the maximum is the same value: "
        "use x > first (not >=) so duplicates do not move into second.")


def test_duplicate_max_later():
    got = ask(3, 5, 1, 5, 5)
    assert got == ["3"], f"For 3 5 1 5 5 expected 3, got {got}. Repeats of 5 must not change anything."


def test_max_last():
    got = ask(3, 1, 8)
    assert got == ["3"], (
        f"For 3 1 8 expected 3, got {got}. When a new maximum arrives, the old maximum becomes the second.")


def test_max_first():
    got = ask(9, 2, 7)
    assert got == ["7"], f"For 9 2 7 expected 7, got {got}. A value below first can still beat second."


def test_all_equal():
    got = ask(6, 6, 6)
    assert got == ["none"], f"6 6 6 has only one distinct value, so print 'none'. Got {got}."


def test_single():
    got = ask(42)
    assert got == ["none"], f"With one number there is no second largest: print 'none'. Got {got}."


def test_two_values():
    assert ask(1, 2) == ["1"], "For 1 2 the second largest is 1."
    assert ask(2, 1) == ["1"], "For 2 1 the second largest is 1."
    assert ask(0, 0) == ["none"], "For 0 0 there is only one distinct value: print 'none'."


def test_all_negative():
    got = ask(-4, -1, -7)
    assert got == ["-4"], (
        f"For -4 -1 -7 expected -4, got {got}. If you got 0, you started second at 0 and treated it as a real value.")


def test_zero_is_a_real_value():
    got = ask(-5, 0, -3)
    assert got == ["-3"], f"For -5 0 -3 expected -3, got {got}."
    got = ask(0, -2)
    assert got == ["-2"], f"For 0 -2 expected -2, got {got}."


@pytest.mark.parametrize("nums", [
    (1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
    (10, 9, 8, 7, 6, 5, 4, 3, 2, 1),
    (7, 7, 3, 3, 7, 3),
    (-1000000000, 1000000000),
    (1000000000, 1000000000, 999999999),
])
def test_various(nums):
    expected = expected_for(nums)
    got = ask(*nums)
    assert got == [expected], f"For {' '.join(map(str, nums))} expected {expected}, got {got}."


def test_long_stream():
    nums = [(i * 7919) % 100003 - 50000 for i in range(100000)]
    expected = expected_for(nums)
    got = ask(*nums)
    assert got == [expected], f"For a stream of 100000 numbers expected {expected}, got {got}."


def test_no_lists():
    tree = ast.parse(SOLUTION.read_text())
    banned_nodes = (ast.List, ast.ListComp, ast.Set, ast.SetComp, ast.Dict, ast.DictComp)
    assert not any(isinstance(node, banned_nodes) for node in ast.walk(tree)), (
        "Do not store the numbers in a list, set or dict. Keep only a few variables and update them as you read.")
    assert not called_names() & {"list", "sorted", "set", "dict", "tuple"}, (
        "Do not use list(), sorted(), set(), dict() or tuple(). Solve it in one pass with a few variables.")
