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

import random
import sys


def ask(a, b, m, timeout=10):
    try:
        return run(f"{a}\n{b}\n{m}\n", timeout=timeout)
    except AssertionError as err:
        if "Exceeds the limit" in str(err) or "int_max_str_digits" in str(err):
            raise AssertionError(
                "Python refuses int() on a string with more than 4300 digits. Do not convert the whole exponent: "
                "process its digits one at a time (r = pow(r, 10, m) * pow(a, d, m) % m), or lift the limit on "
                "purpose with sys.set_int_max_str_digits(0).") from None
        raise


def truth(a, b, m):
    sys.set_int_max_str_digits(0)
    return str(pow(a, int(b), m))


@pytest.mark.parametrize("a, b, m, why", [
    (2, "100", 7, "the example: reducing b mod m gives 4, wrong. 2^100 mod 7 = 2"),
    (5, "0", 13, "exponent 0: the answer is 1"),
    (5, "0", 1, "m = 1: everything is 0, even a^0"),
    (0, "0", 5, "0^0 counts as 1 here"),
    (0, "7", 5, "0^7 = 0"),
    (3, "1", 10, "3^1 mod 10"),
    (3, "10", 1000, "3^10 = 59049, mod 1000 gives 49"),
    (7, "123456789", 10**9 + 7, "a 9-digit exponent"),
    (2, "1000000000000000000000", 10, "powers of 2 mod 10 cycle with period 4: 10^21 mod 4 = 0 so the answer is 6"),
    (10, "5", 1, "m = 1"),
    (6, "100", 12, "m is not prime and gcd(a, m) is not 1: a Fermat shortcut breaks here"),
])
def test_examples(a, b, m, why):
    got = ask(a, b, m)
    assert got == [truth(a, b, m)], f"a={a}, b={b}, m={m}: expected {truth(a, b, m)}, got {got} ({why})."


def test_random_medium():
    rng = random.Random(18)
    for _ in range(60):
        a = rng.randint(0, 10**9)
        b = str(rng.randint(1, 10**30))
        m = rng.randint(1, 10**9 + 7)
        got = ask(a, b, m)
        assert got == [truth(a, b, m)], (
            f"a={a}, b={b}, m={m}: expected {truth(a, b, m)}, got {got}. "
            "Check r = pow(r, 10, m) * pow(a, d, m) % m, and that b is not reduced modulo m.")


@pytest.mark.parametrize("m", [10**9 + 7, 998244353, 1000000000, 12])
def test_hundred_thousand_digits(m):
    rng = random.Random(m)
    b = str(rng.randint(1, 9)) + "".join(rng.choice("0123456789") for _ in range(99999))
    a = rng.randint(2, 10**9)
    got = ask(a, b, m, timeout=8)
    assert got == [truth(a, b, m)], (
        f"100000-digit exponent, m = {m}: expected {truth(a, b, m)}, got {got}. "
        "Process the digits one by one; do not convert the string if you do not lift the digit limit.")
