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

def ask(ms, timeout=10):
    return run(f"{len(ms)}\n" + "".join(f"{s} {e}\n" for s, e in ms), timeout=timeout)


def model(ms):
    for i in range(len(ms)):
        for j in range(i + 1, len(ms)):
            if max(ms[i][0], ms[j][0]) < min(ms[i][1], ms[j][1]):
                return ["NO"]
    return ["YES"]


@pytest.mark.parametrize("ms, why", [
    ([(0, 30), (5, 10), (15, 20)], "the example: nested meetings"),
    ([(7, 10), (2, 4), (4, 7)], "touching meetings are fine"),
    ([], "no meetings"),
    ([(1, 2)], "one meeting"),
    ([(1, 5), (4, 6)], "partial overlap"),
    ([(3, 8), (1, 4)], "unsorted partial overlap"),
    ([(1, 10), (2, 3)], "the long meeting comes first and covers the short one"),
    ([(1, 3), (3, 3 + 1), (2, 3)], "overlap with the first although it is not a neighbour of the second in input order"),
])
def test_examples(ms, why):
    got = ask(ms)
    assert got == model(ms), f"Input {ms}: expected {model(ms)}, got {got} ({why}). Sort by start, then compare each start with the previous end using < (not <=)."


def test_random_small():
    rng = random.Random(25)
    for _ in range(100):
        ms = []
        for _ in range(rng.randint(0, 6)):
            s = rng.randint(0, 15)
            ms.append((s, s + rng.randint(1, 4)))
        assert ask(ms) == model(ms), f"Input {ms}: expected {model(ms)}."


def test_large_yes_and_no():
    ms = [(3 * i, 3 * i + 3) for i in range(200000)]
    random.Random(26).shuffle(ms)
    assert ask(ms) == ["YES"], "200000 back-to-back meetings touch but never overlap: expected YES."
    ms2 = [(3 * i, 3 * i + 3) for i in range(200000)]
    ms2[100000] = (3 * 100000 - 1, 3 * 100000 + 3)
    random.Random(27).shuffle(ms2)
    assert ask(ms2) == ["NO"], "One meeting starts one minute early: expected NO. Too slow? Do not compare all pairs."
