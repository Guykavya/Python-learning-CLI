import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import pytest


def expected(p, r, t, n):
    a = p * (1 + r / (100 * n)) ** (n * t)
    return [f"Amount: {a:,.2f}", f"Interest: {a - p:,.2f}"]


def test_example():
    assert run("1000\n10\n5\n1\n") == ["Amount: 1,610.51", "Interest: 610.51"]


@pytest.mark.parametrize("p, r, t, n", [(1000, 10, 5, 4), (50000, 7.5, 10, 12), (2500.5, 0, 3, 1), (100, 5, 0, 1)])
def test_values(p, r, t, n):
    out = run(f"{p}\n{r}\n{t}\n{n}\n")
    assert out == expected(p, r, t, n), (
        f"For P={p}, R={r}, T={t}, N={n} expected {expected(p, r, t, n)}, got {out}. "
        "Check the brackets: R / (100 * N) inside, and the exponent (N * T) in its own brackets, "
        "because ** binds tighter than *.")


def test_thousands_separator():
    out = run("100000\n12\n2\n1\n")
    assert out[0] == "Amount: 125,440.00", "Use the :,.2f format spec to get commas and 2 decimals."
