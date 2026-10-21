import subprocess
import sys
from pathlib import Path

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

import pytest


def factorize(n):
    """Independent check used only by the tests."""
    parts = []
    m, d = n, 2
    while d * d <= m:
        e = 0
        while m % d == 0:
            m //= d
            e += 1
        if e:
            parts.append(f"{d}" if e == 1 else f"{d}^{e}")
        d += 1
    if m > 1:
        parts.append(f"{m}")
    return f"{n} = " + " * ".join(parts)


@pytest.mark.parametrize("n, expected", [
    (360, "360 = 2^3 * 3^2 * 5"),
    (13, "13 = 13"),
    (2, "2 = 2"),
    (4, "4 = 2^2"),
    (1024, "1024 = 2^10"),
    (12, "12 = 2^2 * 3"),
    (30, "30 = 2 * 3 * 5"),
    (49, "49 = 7^2"),
])
def test_examples(n, expected):
    got = run(f"{n}\n")
    assert got == [expected], (
        f"n = {n}: expected {expected!r}, got {got}. Check the format: ' = ' after n, ' * ' between "
        "factors, p^e only when e > 1, and no ' * ' at the start or end.")


def test_leftover_prime():
    got = run("1999966\n")
    assert got == ["1999966 = 2 * 999983"], (
        f"n = 1999966: expected '1999966 = 2 * 999983', got {got}. After the loop, whatever is left "
        "above 1 is a prime factor and must be printed too.")


def test_mixed_large():
    for n in [999999999999, 10 ** 12, 600851475143]:
        expected = factorize(n)
        got = run(f"{n}\n", timeout=5)
        assert got == [expected], f"n = {n}: expected {expected!r}, got {got}."


def test_large_prime_fast():
    n = 999999999989
    got = run(f"{n}\n", timeout=5)
    assert got == [f"{n} = {n}"], (
        f"n = {n} is prime: expected '{n} = {n}', got {got}. Stop trying divisors once d * d > what is "
        "left; trying every d up to n takes far too long.")


def test_square_of_large_prime_fast():
    n = 999966000289
    got = run(f"{n}\n", timeout=5)
    assert got == [f"{n} = 999983^2"], (
        f"n = {n} = 999983 * 999983: expected '{n} = 999983^2', got {got}. Use d * d <= m (not <), "
        "or a square of a prime is missed.")
