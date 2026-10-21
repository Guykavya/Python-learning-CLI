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



import pytest


@pytest.mark.parametrize("year, expected, why", [
    (2024, "leap", "2024 is divisible by 4 and not by 100"),
    (2023, "not leap", "2023 is not divisible by 4"),
    (1900, "not leap", "1900 is divisible by 100 but not by 400. Checking only % 4 is not enough"),
    (2100, "not leap", "2100 is divisible by 100 but not by 400"),
    (2000, "leap", "2000 is divisible by 400. Check % 400 before % 100"),
    (1600, "leap", "1600 is divisible by 400. Check % 400 before % 100"),
    (4, "leap", "4 is divisible by 4 and not by 100"),
    (1, "not leap", "1 is not divisible by 4"),
    (100, "not leap", "100 is divisible by 100 but not by 400"),
    (400, "leap", "400 is divisible by 400"),
    (1000000000, "leap", "10^9 is divisible by 400"),
    (999999900, "not leap", "999999900 is divisible by 100 but not by 400"),
    (999999996, "leap", "999999996 is divisible by 4 and not by 100"),
])
def test_year(year, expected, why):
    got = run(f"{year}\n")
    assert got == [expected], f"Year {year}: expected {expected!r}, got {got}. {why}."
