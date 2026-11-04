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

def ask(pairs, new, timeout=10):
    return run(f"{len(pairs)}\n" + "".join(f"{l} {r}\n" for l, r in pairs) + f"{new[0]} {new[1]}\n", timeout=timeout)


def model(pairs, new):
    allp = sorted(pairs + [new])
    out = []
    for l, r in allp:
        if out and l <= out[-1][1]:
            out[-1][1] = max(out[-1][1], r)
        else:
            out.append([l, r])
    return [f"{l} {r}" for l, r in out]


@pytest.mark.parametrize("pairs, new, why", [
    ([(1, 2), (3, 5), (6, 7)], (4, 6), "the example: absorbs two intervals"),
    ([], (5, 7), "empty list"),
    ([(1, 5)], (2, 3), "new interval inside an old one"),
    ([(1, 5)], (0, 10), "new interval swallows the old one"),
    ([(1, 2), (5, 6)], (3, 4), "fits between, no touching"),
    ([(1, 2), (5, 6)], (2, 5), "touches both: everything merges"),
    ([(5, 6)], (1, 2), "goes before all"),
    ([(1, 2)], (7, 8), "goes after all"),
    ([(1, 2), (4, 5)], (3, 3), "a single point between: no merge"),
])
def test_examples(pairs, new, why):
    got = ask(pairs, new)
    assert got == model(pairs, new), (
        f"Input {pairs} + {new}: expected {model(pairs, new)}, got {got} ({why}). "
        "Copy r < a, absorb l <= b (touching merges), then copy the rest.")


def test_random_small():
    rng = random.Random(24)
    for _ in range(80):
        cur, pairs = 0, []
        for _ in range(rng.randint(0, 7)):
            l = cur + rng.randint(1, 4)
            r = l + rng.randint(0, 4)
            pairs.append((l, r))
            cur = r + 1
        a = rng.randint(0, 30)
        new = (a, a + rng.randint(0, 8))
        assert ask(pairs, new) == model(pairs, new), f"Input {pairs} + {new}: expected {model(pairs, new)}."


def test_large():
    pairs = [(10 * i, 10 * i + 5) for i in range(200000)]
    new = (999990, 1000030)
    assert ask(pairs, new) == model(pairs, new), "200000 intervals: use one linear scan, not an O(n^2) search."
