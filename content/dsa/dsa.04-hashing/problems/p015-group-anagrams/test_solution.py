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


def ask(words, timeout=10):
    return run(f"{len(words)}\n" + " ".join(words) + "\n", timeout=timeout)


def expected_for(words):
    groups = {}
    for w in words:
        groups.setdefault("".join(sorted(w)), []).append(w)
    result = sorted(sorted(g) for g in groups.values())
    return [" ".join(g) for g in sorted(result, key=lambda g: g[0])]


@pytest.mark.parametrize("words, why", [
    ("eat tea tan ate nat bat".split(), "the example"),
    (["a"], "one word, one group"),
    (["abc", "abc", "cab"], "repeats stay, each listed"),
    (["ab", "abc", "ba"], "different lengths are never anagrams"),
    (["aab", "ab", "aba", "baa"], "aab/aba/baa are anagrams; ab is not (set of letters is the same!)"),
    (["zz", "z", "zzz"], "all different"),
])
def test_examples(words, why):
    got = ask(words)
    assert got == expected_for(words), (
        f"Words {words}: expected {expected_for(words)}, got {got} ({why}). "
        "Sort inside each group and order groups by their first word.")


def test_large():
    rng = random.Random(16)
    words = ["".join(rng.choice("abcdef") for _ in range(rng.randint(1, 6))) for _ in range(100000)]
    got = ask(words)
    assert got == expected_for(words), "Wrong or too slow on 100000 words. Group with a dictionary keyed by the sorted letters."
