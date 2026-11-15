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


def ask(a, timeout=10):
    return run(f"{len(a)}\n" + " ".join(map(str, a)) + "\n", timeout=timeout)


def brute(a):
    values = sorted(set(a))
    best = cur = 0
    for i, v in enumerate(values):
        cur = cur + 1 if i and v == values[i - 1] + 1 else 1
        best = max(best, cur)
    return best


@pytest.mark.parametrize("a, expected, why", [
    ([100, 4, 200, 1, 3, 2], 4, "the example"),
    ([1, 1, 2], 2, "repeats must not lengthen a run"),
    ([5], 1, "one value is a run of length 1"),
    ([1, 3, 5, 7], 1, "no two values are neighbours"),
    ([-2, -1, 0, 1], 4, "a run through zero and negatives"),
    ([9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6], 7, "run 3..9 is the longest"),
])
def test_examples(a, expected, why):
    assert ask(a) == [str(expected)], f"a={a}: expected {expected} ({why})."


def test_empty():
    assert run("0\n\n") == ["0"], "No numbers: the longest run is 0."


def test_random_small():
    rng = random.Random(18)
    for _ in range(40):
        a = [rng.randint(-6, 6) for _ in range(rng.randint(1, 10))]
        assert ask(a) == [str(brute(a))], f"a={a}: expected {brute(a)}."


def test_large_one_run():
    a = list(range(200000))
    random.Random(19).shuffle(a)
    assert ask(a) == ["200000"], (
        "200000 consecutive values in shuffled order. If you start counting from every value you do about 2 * 10^10 steps; "
        "start only at values x with x - 1 missing.")
