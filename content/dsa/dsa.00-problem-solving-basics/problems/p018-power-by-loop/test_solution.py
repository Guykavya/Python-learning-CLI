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


@pytest.mark.parametrize("a, b, expected", [
    (2, 10, 1024),
    (3, 4, 81),
    (-3, 3, -27),
    (-2, 4, 16),
    (7, 1, 7),
    (1, 500, 1),
    (-1, 499, -1),
    (10, 20, 100000000000000000000),
])
def test_examples(a, b, expected):
    got = run(f"{a}\n{b}\n")
    assert got == [str(expected)], (
        f"For a={a}, b={b} expected {expected}, got {got}. "
        "Start the result at 1 and multiply by a exactly b times.")


def test_power_zero():
    got = run("5\n0\n")
    assert got == ["1"], (
        f"5 to the power 0 is 1, got {got}. If the result starts at 1 and the loop runs 0 times, "
        "this works with no special case.")


def test_zero_to_zero():
    got = run("0\n0\n")
    assert got == ["1"], (
        f"0 to the power 0 is defined as 1 here, got {got}. Do not special-case a == 0 before the loop.")


def test_zero_base():
    got = run("0\n5\n")
    assert got == ["0"], f"0 to the power 5 is 0, got {got}."


def test_negative_base_signs():
    assert run("-2\n3\n") == ["-8"], "An odd number of negative factors gives a negative result."
    assert run("-2\n4\n") == ["16"], "An even number of negative factors gives a positive result."


def test_big_exact():
    expected = 1
    for _ in range(200):
        expected *= 2
    got = run("2\n200\n")
    assert got == [str(expected)], (
        "2 to the power 200 must be exact. Keep everything as int: do not use float() or '/'.")


def test_largest():
    expected = 1
    for _ in range(500):
        expected *= -100
    got = run("-100\n500\n")
    assert got == [str(expected)], "(-100) to the power 500 should be exact (a 1 followed by 1000 zeros)."


def test_no_power_operator_or_pow():
    tree = ast.parse(SOLUTION.read_text())
    assert not any(isinstance(n, ast.Pow) for n in ast.walk(tree)), (
        "Do not use the ** operator (or **=). Build the power with a loop of multiplications.")
    assert "pow" not in called_names(), "Do not call pow(). Build the power with a loop."
    assert not any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree)), (
        "Do not import anything. Only a loop and * are needed.")
