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


def primes_upto(n):
    """Test-side helper (a sieve) to compute the expected answer."""
    if n < 2:
        return []
    mark = [True] * (n + 1)
    mark[0] = mark[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if mark[i]:
            for j in range(i * i, n + 1, i):
                mark[j] = False
    return [i for i in range(n + 1) if mark[i]]


def expected_lines(n):
    p = primes_upto(n)
    if not p:
        return ["count 0"]
    return [" ".join(map(str, p)), f"count {len(p)}"]


def test_ten():
    got = run("10\n")
    assert got == ["2 3 5 7", "count 4"], f"For n = 10 expected ['2 3 5 7', 'count 4'], got {got}"


def test_hundred():
    got = run("100\n")
    assert got == expected_lines(100), (
        f"For n = 100 there are 25 primes.\nExpected: {expected_lines(100)}\nGot: {got}")


def test_two():
    got = run("2\n")
    assert got == ["2", "count 1"], (
        f"For n = 2 the only prime is 2 itself (include n when it is prime). Expected ['2', 'count 1'], got {got}")


@pytest.mark.parametrize("n", [0, 1])
def test_no_primes(n):
    got = run(f"{n}\n")
    assert got == ["count 0"], (
        f"For n = {n} there are no primes (1 is not prime). Print only 'count 0'. Got {got}")


def test_square_of_prime():
    got = run("25\n")
    assert got == expected_lines(25), (
        f"For n = 25 expected {expected_lines(25)}, got {got}. "
        "If 25 appears in your list, your divisor loop stops too early: use d * d <= x, not d * d < x.")


@pytest.mark.parametrize("n", [3, 4, 49, 50, 997])
def test_small(n):
    got = run(f"{n}\n")
    exp = expected_lines(n)
    assert got == exp, f"For n = {n}:\nExpected: {exp}\nGot: {got}"


def test_large_is_fast():
    got = run("200000\n", timeout=10)
    exp = expected_lines(200000)
    assert len(got) == 2 and got[1] == exp[1], (
        f"For n = 200000 expected the last line {exp[1]!r}, got {got[-1] if got else 'nothing'!r}")
    assert got[0] == exp[0], "For n = 200000 the list of primes is wrong (count is right, so check the order or spacing)."
