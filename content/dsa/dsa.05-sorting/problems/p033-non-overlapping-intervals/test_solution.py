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

def ask(iv, timeout=10):
    return run(f"{len(iv)}\n" + "".join(f"{a} {b}\n" for a, b in iv), timeout=timeout)


def brute(iv):
    n = len(iv)
    best = 0
    for mask in range(1 << n):
        chosen = sorted(iv[i] for i in range(n) if mask >> i & 1)
        if all(chosen[k][1] <= chosen[k + 1][0] for k in range(len(chosen) - 1)):
            best = max(best, len(chosen))
    return n - best


@pytest.mark.parametrize("iv, why", [
    ([(1, 2), (2, 3), (3, 4), (1, 3)], "the example: remove [1,3)"),
    ([(1, 2), (1, 2), (1, 2)], "identical intervals: keep one"),
    ([(1, 2), (2, 3)], "touching: nothing to remove"),
    ([], "empty"),
    ([(1, 100), (11, 22), (1, 11), (2, 12)], "a long first interval blocks the others"),
    ([(0, 2), (1, 3), (2, 4), (3, 5)], "chain"),
    ([(-5, -1), (-3, 2), (1, 4)], "negative coordinates"),
])
def test_examples(iv, why):
    got = ask(iv)
    assert got == [str(brute(iv))], f"Input {iv}: expected {brute(iv)}, got {got} ({why}). Sort by END; keep an interval when l >= last kept end."


def test_random_small():
    rng = random.Random(42)
    for _ in range(100):
        iv = []
        for _ in range(rng.randint(0, 9)):
            a = rng.randint(0, 12)
            iv.append((a, a + rng.randint(1, 5)))
        assert ask(iv) == [str(brute(iv))], f"Input {iv}: expected {brute(iv)}."


def test_large():
    rng = random.Random(43)
    iv = []
    for _ in range(200000):
        a = rng.randint(0, 10**9 - 3000)
        iv.append((a, a + rng.randint(1, 3000)))
    kept, last = 0, -10**18
    for a, b in sorted(iv, key=lambda x: x[1]):
        if a >= last:
            kept += 1
            last = b
    assert ask(iv) == [str(200000 - kept)], "Wrong or too slow on 200000 intervals."
