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

MOD = 10**9 + 7


def ask(values, timeout=10):
    return run(f"{len(values)}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def brute(values):
    out = []
    for i in range(len(values)):
        p = 1
        for j, v in enumerate(values):
            if j != i:
                p = p * v % MOD
        out.append(str(p))
    return [" ".join(out)]


def by_inverse(values):
    """The division method with modular inverses and the zero cases: an independent check."""
    zeros = [i for i, v in enumerate(values) if v % MOD == 0]
    nonzero_product = 1
    for v in values:
        if v % MOD:
            nonzero_product = nonzero_product * v % MOD
    if len(zeros) >= 2:
        out = [0] * len(values)
    elif len(zeros) == 1:
        out = [0] * len(values)
        out[zeros[0]] = nonzero_product
    else:
        out = [nonzero_product * pow(v % MOD, MOD - 2, MOD) % MOD for v in values]
    return [" ".join(map(str, out))]


@pytest.mark.parametrize("values, expected, why", [
    ([1, 2, 3, 4], "24 12 8 6", "the example"),
    ([2, 0, 3], "0 6 0", "one zero: only the zero's position has a non-zero product. Division would crash here"),
    ([0, 4, 0], "0 0 0", "two zeros: every product contains at least one zero"),
    ([-1, 2], "2 1000000006", "a negative product is printed modulo 10^9 + 7, as a non-negative number"),
    ([5], "1", "one element: the product of nothing is 1"),
    ([3, 3], "3 3", "two equal values"),
    ([-2, -3, -4], "12 8 6", "negative numbers: two negatives make a positive"),
    ([10**9, 10**9, 10**9], f"{10**18 % MOD} {10**18 % MOD} {10**18 % MOD}", "reduce modulo 10^9 + 7"),
])
def test_examples(values, expected, why):
    got = ask(values)
    assert got == [expected], f"Input {values}: expected {expected!r}, got {got} ({why})."


def test_random_small_against_brute_force():
    rng = random.Random(40)
    for _ in range(50):
        values = [rng.randint(-5, 5) for _ in range(rng.randint(1, 10))]
        got = ask(values)
        expected = brute(values)
        assert got == expected, (
            f"Input {values}: expected {expected}, got {got}. Store the left product BEFORE multiplying by a[i], "
            "and take % MOD so negatives become non-negative.")


@pytest.mark.parametrize("zeros", [0, 1, 2])
def test_large(zeros):
    rng = random.Random(4040 + zeros)
    values = [rng.choice((-1, 1)) * rng.randint(1, 10**9) for _ in range(200000)]
    for k in range(zeros):
        values[rng.randrange(len(values))] = 0
    expected = by_inverse(values)
    got = ask(values, timeout=10)
    assert got == expected, (
        f"200000 values with {zeros} zero(s): the products are wrong. A timeout means you multiply all the other "
        "numbers for every position (O(n^2)) or skip % MOD and let the numbers grow huge.")
