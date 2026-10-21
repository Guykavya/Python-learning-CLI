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


def ask(t, values, timeout=10):
    return run(f"{len(values)} {t}\n" + " ".join(map(str, values)) + "\n", timeout=timeout)


def brute(t, values):
    for j in range(len(values)):
        for i in range(j):
            if values[i] + values[j] == t:
                return [f"{i + 1} {j + 1}"]
    return ["none"]


@pytest.mark.parametrize("t, values, expected, why", [
    (9, [2, 7, 11, 15, -2], "1 2", "2 + 7 = 9"),
    (6, [3, 1, 3, 5], "1 3", "3 + 3 at positions 1 and 3 finishes earlier (j = 3) than 1 + 5 (j = 4)"),
    (10, [5, 1, 2], "none", "5 + 5 would need two different positions holding 5"),
    (4, [2, 2, 2, 2], "1 2", "smallest j is 2; the earliest i is 1"),
    (0, [-3, 4, 3, -4], "1 3", "-3 + 3 = 0 with negative numbers"),
    (8, [4], "none", "one number cannot form a pair"),
    (5, [1, 4, 4, 1], "1 2", "the first pair found by j is (1, 2)"),
    (7, [5, 2, 6, 1, 4, 3], "1 2", "5 + 2"),
    (7, [6, 3, 4, 1], "2 3", "3 + 4 at j = 3 comes before 6 + 1 at j = 4"),
    (7, [2, 2, 5], "1 3", "for j = 3 the earliest i holding 2 is 1, so keep the FIRST position of each value"),
])
def test_examples(t, values, expected, why):
    got = ask(t, values)
    assert got == [expected], f"t = {t}, values {values}: expected {expected}, got {got} ({why})."


def test_random_against_all_pairs():
    rng = random.Random(10)
    for _ in range(15):
        values = [rng.randint(-6, 6) for _ in range(rng.randint(1, 12))]
        t = rng.randint(-8, 8)
        got = ask(t, values)
        assert got == brute(t, values), (
            f"t = {t}, values {values}: expected {brute(t, values)}, got {got}. "
            "Check the tie rule: smallest j first, then smallest i, so store the FIRST position of each value.")


def test_large_no_pair():
    values = [2 * i for i in range(200000)]        # all even, target odd: no pair exists
    got = ask(1, values, timeout=5)
    assert got == ["none"], (
        f"200000 even numbers, odd target: expected ['none'], got {got}. If this timed out, you still try every pair. "
        "For each value, look up the value it needs in a dict of values seen so far.")


def test_large_pair_at_the_end():
    values = [10**6 + i for i in range(200000)]    # all large: any two of them sum to far more than 12
    values[150000] = 5
    values[-1] = 7
    got = ask(12, values, timeout=5)
    assert got == ["150001 200000"], (
        f"Large input whose only pair is at positions 150001 and 200000: got {got}.")
