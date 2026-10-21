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


def collatz(n: int) -> tuple[int, int]:
    steps, peak = 0, n
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
        peak = max(peak, n)
    return steps, peak


def test_six():
    got = run("6\n")
    assert got == ["steps 8", "peak 16"], (
        f"6 -> 3 -> 10 -> 5 -> 16 -> 8 -> 4 -> 2 -> 1 is 8 steps with peak 16. Got {got}. "
        "Print exactly 'steps S' then 'peak P'.")


def test_one():
    got = run("1\n")
    assert got == ["steps 0", "peak 1"], (
        f"1 is already 1: no steps, and the peak is the start, 1. Got {got}.")


def test_two():
    got = run("2\n")
    assert got == ["steps 1", "peak 2"], f"2 -> 1 is one step; peak 2. Got {got}."


def test_peak_is_start():
    got = run("8\n")
    assert got == ["steps 3", "peak 8"], (
        f"8 -> 4 -> 2 -> 1: 3 steps, and the largest value is the starting 8. Got {got}. "
        "Start peak at n, not at 0 or 1.")


def test_twenty_seven():
    got = run("27\n")
    assert got == ["steps 111", "peak 9232"], (
        f"27 takes 111 steps and climbs to 9232. Got {got}. If you see 9232.0, use // instead of /.")


@pytest.mark.parametrize("n", [3, 7, 97, 871, 1000000000000, 999999999999, 989345275647])
def test_various(n):
    s, p = collatz(n)
    got = run(f"{n}\n")
    assert got == [f"steps {s}", f"peak {p}"], f"For n={n} expected steps {s}, peak {p}; got {got}."


@pytest.mark.parametrize("n", [319804831, 77566362559])
def test_huge_peak_needs_exact_integers(n):
    s, p = collatz(n)
    got = run(f"{n}\n")
    assert got == [f"steps {s}", f"peak {p}"], (
        f"For n={n} expected steps {s}, peak {p}; got {got}. The values here grow past 10^18. "
        "With / the number becomes a float and loses exactness; use // to halve.")
