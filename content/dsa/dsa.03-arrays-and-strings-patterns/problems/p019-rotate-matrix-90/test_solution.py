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


def ask(g, k, timeout=10):
    text = f"{len(g)} {k}\n" + "".join(" ".join(map(str, row)) + "\n" for row in g)
    return run(text, timeout=timeout)


def rotated(g, k):
    """A second algorithm: build the turned grid with zip (rows reversed, then columns)."""
    for _ in range(k % 4):
        g = [list(col) for col in zip(*g[::-1])]
    return [" ".join(map(str, row)) for row in g]


G3 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


@pytest.mark.parametrize("g, k, expected, why", [
    (G3, 1, ["7 4 1", "8 5 2", "9 6 3"], "the example: one clockwise turn"),
    (G3, 2, ["9 8 7", "6 5 4", "3 2 1"], "two turns: 180 degrees"),
    (G3, 3, ["3 6 9", "2 5 8", "1 4 7"], "three clockwise turns = one counter-clockwise turn"),
    (G3, 0, ["1 2 3", "4 5 6", "7 8 9"], "k = 0: unchanged"),
    (G3, 4, ["1 2 3", "4 5 6", "7 8 9"], "k = 4: back to the start"),
    ([[1, 2], [3, 4]], 1, ["3 1", "4 2"], "2 x 2 clockwise: 1 moves to the top right. If you got 2 4 / 1 3 you turned counter-clockwise"),
    ([[5]], 7, ["5"], "1 x 1 never changes"),
    ([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]], 1,
     ["13 9 5 1", "14 10 6 2", "15 11 7 3", "16 12 8 4"], "4 x 4 (even size): the inner 2 x 2 turns too"),
])
def test_examples(g, k, expected, why):
    got = ask(g, k)
    assert got == expected, f"Grid {g}, k = {k}: expected {expected}, got {got} ({why})."


def test_random():
    rng = random.Random(27)
    for _ in range(20):
        n = rng.randint(1, 6)
        g = [[rng.randint(0, 99) for _ in range(n)] for _ in range(n)]
        k = rng.randint(0, 9)
        got = ask(g, k)
        assert got == rotated(g, k), f"Grid {g}, k = {k}: expected {rotated(g, k)}, got {got}."


def test_huge_k():
    got = ask(G3, 10**9 + 1)
    assert got == ["7 4 1", "8 5 2", "9 6 3"], (
        f"k = 1000000001 is 1 more than a multiple of 4, so it is one turn. Got {got}. "
        "If this timed out you turn the grid k times; use k % 4.")


def test_large_grid():
    rng = random.Random(28)
    g = [[rng.randint(0, 10**6) for _ in range(500)] for _ in range(500)]
    got = ask(g, 999999999, timeout=10)
    assert got == rotated(g, 3), (
        "A 500 x 500 grid with k = 999999999 (3 turns): wrong or too slow. Use k % 4 and O(n^2) work per turn.")
