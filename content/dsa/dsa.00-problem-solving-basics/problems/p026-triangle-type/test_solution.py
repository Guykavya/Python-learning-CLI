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


def ask(a: int, b: int, c: int) -> list[str]:
    return run(f"{a}\n{b}\n{c}\n")


@pytest.mark.parametrize("sides", [(3, 4, 5), (5, 3, 4), (4, 5, 3), (5, 12, 13), (13, 12, 5), (8, 15, 17)])
def test_right_scalene_any_order(sides):
    got = ask(*sides)
    assert got == ["scalene", "right"], (
        f"{sides} is a right scalene triangle, got {got}. "
        "The largest side may be any of the three inputs; compare it with the other two.")


def test_isosceles():
    got = ask(2, 2, 3)
    assert got == ["isosceles", "not right"], f"2 2 3 has exactly two equal sides. Got {got}."
    got = ask(3, 2, 3)
    assert got == ["isosceles", "not right"], f"3 2 3: the equal sides are a and c. Got {got}."
    got = ask(10, 6, 6)
    assert got == ["isosceles", "not right"], f"10 6 6: the equal sides are b and c (6 + 6 > 10). Got {got}."


def test_equilateral():
    got = ask(7, 7, 7)
    assert got == ["equilateral", "not right"], (
        f"7 7 7 is equilateral, got {got}. Test 'all three equal' before 'two equal'.")


def test_scalene_not_right():
    got = ask(4, 5, 6)
    assert got == ["scalene", "not right"], f"4 5 6: all different, 16 + 25 != 36. Got {got}."


@pytest.mark.parametrize("sides", [(1, 2, 3), (3, 1, 2), (2, 3, 5), (5, 5, 10)])
def test_degenerate_invalid(sides):
    got = ask(*sides)
    assert got == ["invalid"], (
        f"{sides}: the largest side equals the sum of the other two, so the triangle is flat. "
        f"Print only 'invalid'. Got {got}. Use >= in the validity check.")


@pytest.mark.parametrize("sides", [(1, 2, 10), (100, 1, 1)])
def test_too_long_invalid(sides):
    got = ask(*sides)
    assert got == ["invalid"], f"{sides}: one side is longer than the other two together. Got {got}."


@pytest.mark.parametrize("sides", [(0, 4, 4), (0, 0, 0), (-3, 4, 5), (5, 5, -1), (-5, -5, -5), (10, 10, -1)])
def test_non_positive_invalid(sides):
    got = ask(*sides)
    assert got == ["invalid"], f"{sides} has a side that is not positive, so print 'invalid'. Got {got}."


def test_big_right():
    got = ask(600000000, 800000000, 1000000000)
    assert got == ["scalene", "right"], (
        f"600000000 800000000 1000000000 is a scaled 3-4-5 triangle. Got {got}. "
        "Use integer arithmetic (no sqrt, no floats).")


def test_big_almost_right():
    got = ask(600000000, 800000000, 999999999)
    assert got == ["scalene", "not right"], (
        f"999999999 is just short of the right-angle length, so this is not right. Got {got}. "
        "Floats or square roots can round this the wrong way.")


def test_big_equilateral_and_isosceles():
    assert ask(1000000000, 1000000000, 1000000000) == ["equilateral", "not right"], "Large equal sides are equilateral."
    assert ask(1000000000, 1000000000, 1) == ["isosceles", "not right"], "1000000000 1000000000 1 is a valid thin isosceles triangle."
