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


@pytest.mark.parametrize("words, why", [
    (["pear", "fig", "apple", "kiwi", "date", "plum"], "the example"),
    (["b", "a"], "equal length: keep input order, do not sort alphabetically"),
    (["x"], "one word"),
    (["ccc", "bb", "a", "dd", "e", "fff"], "several ties"),
    (["zz", "yy", "xx"], "all equal length, reverse alphabetical input"),
])
def test_examples(words, why):
    want = [" ".join(sorted(words, key=len))]
    got = ask(words)
    assert got == want, (
        f"Input {words}: expected {want}, got {got} ({why}). Sort by length only; ties must keep the input order.")


def test_large():
    rng = random.Random(2)
    words = ["".join(rng.choice("abc") for _ in range(rng.randint(1, 20))) for _ in range(100000)]
    want = [" ".join(sorted(words, key=len))]
    assert ask(words) == want, "Wrong or too slow on 100000 words. Equal-length words must keep their input order."
