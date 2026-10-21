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


def brute(a: int, b: int, k: int) -> int:
    return sum(1 for x in range(a, b + 1) if x % k == 0)


@pytest.mark.parametrize("a, b, k", [
    (1, 10, 3),
    (2, 20, 5),
    (1, 100, 7),
    (10, 11, 4),
])
def test_basic(a, b, k):
    expected = brute(a, b, k)
    got = run(f"{a}\n{b}\n{k}\n")
    assert got == [str(expected)], f"For a={a}, b={b}, k={k} expected {expected}, got {got}."


def test_both_ends_included():
    got = run("3\n9\n3\n")
    assert got == ["3"], (
        f"3, 6 and 9 are all multiples of 3, got {got}. Both ends are included: use range(a, b + 1).")


def test_single_number_divisible():
    got = run("12\n12\n4\n")
    assert got == ["1"], f"When a == b == 12 and k = 4, the one number counts. Expected 1, got {got}."


def test_single_number_not_divisible():
    got = run("7\n7\n2\n")
    assert got == ["0"], f"When a == b == 7 and k = 2, nothing counts. Expected 0, got {got}."


def test_negatives():
    got = run("-6\n6\n3\n")
    assert got == ["5"], (
        f"-6, -3, 0, 3, 6 are the multiples of 3 here. Expected 5, got {got}. "
        "Negative numbers and 0 can be divisible too.")


def test_all_negative():
    got = run("-20\n-1\n5\n")
    assert got == ["4"], f"-20, -15, -10, -5. Expected 4, got {got}."


def test_k_is_one():
    got = run("4\n8\n1\n")
    assert got == ["5"], f"Every number is divisible by 1, so the answer is b - a + 1 = 5. Got {got}."


def test_k_bigger_than_range():
    assert run("1\n5\n100\n") == ["0"], "No multiple of 100 lies between 1 and 5."
    assert run("-5\n5\n100\n") == ["1"], "0 is a multiple of every k, and it lies between -5 and 5."


def test_full_range():
    got = run("-1000000\n1000000\n7\n", timeout=10)
    expected = 1000000 // 7 - (-1000001) // 7
    assert got == [str(expected)], f"Largest range with k=7: expected {expected}, got {got}."
