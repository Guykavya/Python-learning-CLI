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


def ask(s, L, timeout=10):
    return run(f"{s}\n{L}\n", timeout=timeout)


def expected_for(s, L):
    seen, rep = set(), set()
    for i in range(len(s) - L + 1):
        seg = s[i:i + L]
        (rep if seg in seen else seen).add(seg)
    r = sorted(rep)
    return [str(len(r))] + ([" ".join(r)] if r else [])


@pytest.mark.parametrize("s, L, why", [
    ("AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT", 10, "the example"),
    ("AAAA", 2, "overlapping occurrences: AA occurs three times but is reported once"),
    ("ACGT", 2, "no repeats: print 0 and an empty line"),
    ("AAAAAAAAAAAAA", 10, "overlap: AAAAAAAAAA occurs 4 times, reported once"),
    ("ACGTACGT", 4, "a segment that occurs twice, not overlapping"),
    ("ACG", 3, "the only window is the whole string"),
])
def test_examples(s, L, why):
    assert ask(s, L) == expected_for(s, L), (
        f"s={s!r}, L={L}: expected {expected_for(s, L)} ({why}). Report each repeated segment once, sorted.")


def test_random_small():
    rng = random.Random(24)
    for _ in range(40):
        s = "".join(rng.choice("AC") for _ in range(rng.randint(3, 14)))
        L = rng.randint(1, 4)
        assert ask(s, L) == expected_for(s, L), f"s={s!r}, L={L}: expected {expected_for(s, L)}."


def test_large():
    rng = random.Random(25)
    s = "".join(rng.choice("ACGT") for _ in range(200000))
    assert ask(s, 10) == expected_for(s, 10), "200000 letters, L = 10: one pass with two sets is enough."
