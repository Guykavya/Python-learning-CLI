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


def brute(ms):
    if not ms:
        return 0
    return max(sum(1 for s, e in ms if s <= t < e) for t in range(0, max(e for _, e in ms)))


@pytest.mark.parametrize("ms, why", [
    ([(0, 30), (5, 10), (15, 20)], "the example: 2 rooms"),
    ([(7, 10), (2, 4), (4, 7)], "touching meetings share a room: 1"),
    ([], "no meetings: 0 rooms"),
    ([(1, 2)], "one meeting"),
    ([(1, 10), (2, 3), (4, 5)], "nested meetings, neighbours do not overlap but both overlap the long one: 2"),
    ([(1, 5), (1, 5), (1, 5)], "identical meetings: 3"),
    ([(1, 3), (2, 4), (3, 5)], "a chain: the middle one overlaps both, but only 2 at a time"),
])
def test_examples(ms, why):
    got = ask(ms)
    assert got == [str(brute(ms))], f"Input {ms}: expected {brute(ms)}, got {got} ({why}). Free a room when end <= next start."


def test_random_small():
    rng = random.Random(38)
    for _ in range(100):
        ms = []
        for _ in range(rng.randint(0, 8)):
            s = rng.randint(0, 12)
            ms.append((s, s + rng.randint(1, 6)))
        assert ask(ms) == [str(brute(ms))], f"Input {ms}: expected {brute(ms)}."


def test_large():
    rng = random.Random(39)
    ms = []
    for _ in range(200000):
        s = rng.randint(0, 10**6)
        ms.append((s, s + rng.randint(1, 1000)))
    ev = sorted([(s, 1) for s, e in ms] + [(e, -1) for s, e in ms])
    cur = best = 0
    for _, d in ev:
        cur += d
        best = max(best, cur)
    assert ask(ms) == [str(best)], "Wrong or too slow on 200000 meetings. Sort, then sweep once."


def test_all_identical_large():
    ms = [(5, 9)] * 200000
    assert ask(ms) == ["200000"], "200000 identical meetings need 200000 rooms."
