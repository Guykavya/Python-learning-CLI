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

def ask(values, timeout=10):
    return run(f"{len(values)}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)

from itertools import permutations
from functools import cmp_to_key


def brute(values):
    return max("".join(map(str, p)) for p in permutations(values)).lstrip("0") or "0"


def fast(values):
    def cmp(x, y):
        return -1 if x + y > y + x else (1 if x + y < y + x else 0)
    s = "".join(sorted(map(str, values), key=cmp_to_key(cmp)))
    return "0" if s[0] == "0" else s


@pytest.mark.parametrize("values, why", [
    ([3, 30, 34, 5, 9], "the example"),
    ([0, 0, 0], "all zeros: print 0"),
    ([10, 2], "'210' beats '102'"),
    ([3, 34], "34 before 3: '343' > '334'"),
    ([121, 12], "'12121' vs '12112'"),
    ([8308, 830], "'8308830' vs '8308308'"),
    ([5], "one number"),
    ([0, 1], "'10' beats '01'"),
])
def test_examples(values, why):
    got = ask(values)
    assert got == [brute(values)], f"Input {values}: expected {brute(values)}, got {got} ({why}). Order a before b when a+b > b+a as strings."


def test_random_small():
    rng = random.Random(28)
    for _ in range(80):
        values = [rng.choice([0, 1, 2, 3, 12, 21, 31, 313, 99, 9]) for _ in range(rng.randint(1, 6))]
        assert ask(values) == [brute(values)], f"Input {values}: expected {brute(values)}."


def test_large():
    rng = random.Random(29)
    values = [rng.randint(0, 10**9) for _ in range(100000)]
    assert ask(values) == [fast(values)], "Wrong or too slow on 100000 numbers."
