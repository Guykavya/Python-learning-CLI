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


@pytest.mark.parametrize("values, expected, why", [
    ([4, 1, 2, 1, 2], 4, "1 and 2 cancel"),
    ([9], 9, "a single number is the answer"),
    ([7, 7, 0], 0, "the single value can be 0: start your accumulator at 0 and still print 0"),
    ([5, 3, 5], 3, "the copies of 5 are not next to each other"),
    ([1, 2, 3, 2, 1], 3, "pairs around the single number"),
    ([2 ** 29, 5, 2 ** 29], 5, "large values"),
])
def test_examples(values, expected, why):
    got = ask(values)
    assert got == [str(expected)], f"values {values}: expected {expected}, got {got} ({why})."


def test_random_shuffled():
    rng = random.Random(24)
    for _ in range(10):
        pairs = [rng.randint(0, 50) for _ in range(rng.randint(0, 12))]
        single = rng.randint(0, 50)
        values = pairs + pairs + [single]
        rng.shuffle(values)
        if single in pairs:
            continue
        got = ask(values)
        assert got == [str(single)], f"values {values}: expected {single}, got {got}. XOR all values; pairs cancel in any order."


def test_large():
    rng = random.Random(240)
    pairs = rng.sample(range(1, 2 ** 30), 499999)
    single = 0
    values = pairs + pairs + [single]
    rng.shuffle(values)
    got = ask(values, timeout=5)
    assert got == [str(single)], (
        f"999999 numbers: expected {single}, got {got}. If this timed out, you are probably calling `count` or `in` on "
        "a list inside a loop (a hidden O(n) each). XOR everything in one pass instead.")
