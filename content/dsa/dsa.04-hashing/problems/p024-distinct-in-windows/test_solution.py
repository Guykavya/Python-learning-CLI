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


def ask(a, k, timeout=10):
    return run(f"{len(a)} {k}\n" + " ".join(map(str, a)) + "\n", timeout=timeout)


def expected_for(a, k):
    return [" ".join(str(len(set(a[i:i + k]))) for i in range(len(a) - k + 1))]


@pytest.mark.parametrize("a, k, why", [
    ([1, 2, 1, 3, 4, 2, 3], 4, "the example"),
    ([5], 1, "one element"),
    ([7, 7, 7, 7], 2, "all equal: one distinct in every window"),
    ([1, 2, 3, 4], 4, "k = n: one window"),
    ([1, 2, 3, 4], 1, "k = 1: every window has one value"),
    ([1, 1, 2, 2, 3, 3], 3, "values leave the window one by one"),
])
def test_examples(a, k, why):
    assert ask(a, k) == expected_for(a, k), (
        f"a={a}, k={k}: expected {expected_for(a, k)} ({why}). Delete a key when its count drops to 0.")


def test_random_small():
    rng = random.Random(27)
    for _ in range(40):
        a = [rng.randint(0, 4) for _ in range(rng.randint(1, 12))]
        k = rng.randint(1, len(a))
        assert ask(a, k) == expected_for(a, k), f"a={a}, k={k}: expected {expected_for(a, k)}."


def test_large():
    rng = random.Random(28)
    n, k = 200000, 1000
    a = [rng.randint(0, 5000) for _ in range(n)]
    count, out = {}, []
    for x in a[:k]:
        count[x] = count.get(x, 0) + 1
    out.append(len(count))
    for i in range(k, n):
        count[a[i]] = count.get(a[i], 0) + 1
        count[a[i - k]] -= 1
        if count[a[i - k]] == 0:
            del count[a[i - k]]
        out.append(len(count))
    assert ask(a, k) == [" ".join(map(str, out))], (
        "n = 200000, k = 1000: building a set per window is about 2 * 10^8 steps. Slide one dictionary instead.")
