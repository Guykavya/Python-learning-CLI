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


def ask(a, b, timeout=10):
    text = f"{len(a)}\n" + " ".join(map(str, a)) + f"\n{len(b)}\n" + " ".join(map(str, b)) + "\n"
    return run(text, timeout=timeout)


def merged(a, b):
    out = sorted(a + b)
    return [" ".join(map(str, out))] if out else []


@pytest.mark.parametrize("a, b, why", [
    ([1, 4, 4, 9], [2, 4, 10], "the example"),
    ([1, 2, 3], [7, 8, 9], "all of a comes first: after a runs out, copy the rest of b"),
    ([7, 8, 9], [1, 2, 3], "all of b comes first: after b runs out, copy the rest of a"),
    ([1, 3, 5, 7], [2], "b runs out early; a's tail 3 5 7 must still be printed"),
    ([5], [1, 2, 3, 4, 6], "one element in the middle of the other array"),
    ([2, 2, 2], [2, 2], "all values equal: the loop must still advance on ties"),
    ([-5, 0, 5], [-10, 10], "negative values"),
])
def test_examples(a, b, why):
    got = ask(a, b)
    assert got == merged(a, b), f"a = {a}, b = {b}: expected {merged(a, b)}, got {got} ({why})."


def test_one_empty():
    got = ask([], [3, 4])
    assert got == ["3 4"], f"a is empty (n = 0, empty line): expected ['3 4'], got {got}. Copy what is left of b."
    got = ask([1, 9], [])
    assert got == ["1 9"], f"b is empty (m = 0, empty line): expected ['1 9'], got {got}. Copy what is left of a."


def test_both_empty():
    got = ask([], [])
    assert got == [], f"Both arrays empty: print an empty line. Got {got}."


def test_random_small():
    rng = random.Random(12)
    for _ in range(25):
        a = sorted(rng.randint(-9, 9) for _ in range(rng.randint(0, 8)))
        b = sorted(rng.randint(-9, 9) for _ in range(rng.randint(0, 8)))
        got = ask(a, b)
        assert got == merged(a, b), (
            f"a = {a}, b = {b}: expected {merged(a, b)}, got {got}. Check the tail copy after the main loop.")


def test_large():
    rng = random.Random(13)
    a = sorted(rng.randint(-10**9, 10**9) for _ in range(200000))
    b = sorted(rng.randint(-10**9, 10**9) for _ in range(200000))
    got = ask(a, b, timeout=10)
    assert got == merged(a, b), (
        "Two sorted arrays of 200000 elements each were not merged correctly or fast enough. "
        "Do not use list.pop(0) or insert(): each one shifts the whole list (O(n) per step).")
