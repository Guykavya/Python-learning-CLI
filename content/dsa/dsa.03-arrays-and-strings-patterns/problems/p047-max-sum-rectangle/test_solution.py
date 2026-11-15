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


def ask(grid, timeout=10):
    text = f"{len(grid)} {len(grid[0])}\n" + "\n".join(" ".join(map(str, row)) for row in grid) + "\n"
    return run(text, timeout=timeout)


def brute(g):
    r, c = len(g), len(g[0])
    best = None
    for t in range(r):
        for b in range(t, r):
            for le in range(c):
                for ri in range(le, c):
                    s = sum(g[i][j] for i in range(t, b + 1) for j in range(le, ri + 1))
                    if best is None or s > best:
                        best = s
    return best


def by_column_pairs(g):
    """Independent check: fix LEFT and RIGHT columns, prefix sums down the rows, best = P[b] - min P[t]."""
    r, c = len(g), len(g[0])
    best = None
    for le in range(c):
        rows = [0] * r
        for ri in range(le, c):
            for i in range(r):
                rows[i] += g[i][ri]
            pre, low = 0, 0
            for i in range(r):
                pre += rows[i]
                if best is None or pre - low > best:
                    best = pre - low
                if pre < low:
                    low = pre
    return best


EXAMPLE = [[1, 2, -1, -4, -20], [-8, -3, 4, 2, 1], [3, 8, 10, 1, 3], [-4, -1, 1, 7, -6]]


@pytest.mark.parametrize("grid, want, why", [
    (EXAMPLE, 29, "the example"),
    ([[5]], 5, "a 1 x 1 grid"),
    ([[-7]], -7, "a single negative cell: the rectangle cannot be empty"),
    ([[-3, -1], [-4, -2]], -1, "all negative: the best rectangle is the largest single cell"),
    ([[1, 2], [3, 4]], 10, "all positive: the whole grid"),
    ([[2, -1, 2, -9, 4]], 4, "one row: plain Kadane (4 beats 2 - 1 + 2 = 3)"),
    ([[2], [-1], [2], [-9], [4]], 4, "one column: the band of rows matters, Kadane over a single column sum"),
    ([[1, -10, 1], [1, -10, 1], [1, -10, 1]], 3, "two separate columns of 1s: they cannot join across the -10s"),
    ([[1, 1, -5], [1, 1, -5], [-5, -5, 9]], 9, "a single big corner cell beats the 2 x 2 block of ones (sum 4)"),
])
def test_examples(grid, want, why):
    got = ask(grid)
    assert got == [str(want)], f"Grid {grid}: expected {want}, got {got} ({why})."


def test_non_square_rectangle():
    g = [[0, 0, 0, 0], [3, 3, 3, 3], [0, 0, 0, 0]]
    assert ask(g) == ["12"], (
        "The best rectangle is the middle row, 1 x 4 (sum 12). Make sure you try every band of rows and every "
        "stretch of columns, not only squares.")


def test_column_sums_reset_for_each_top():
    g = [[10, 10], [-100, -100], [1, 1]]
    assert ask(g) == ["20"], (
        "Expected 20 (the top row). If you get less, the column sums carry over from one top row to the next: "
        "reset them to 0 whenever the top row changes.")


def test_random_small_against_brute_force():
    rng = random.Random(47)
    for _ in range(20):
        r, c = rng.randint(1, 5), rng.randint(1, 5)
        g = [[rng.randint(-9, 9) for _ in range(c)] for _ in range(r)]
        got = ask(g)
        assert got == [str(brute(g))], f"Grid {g}: expected {brute(g)}, got {got}."


def test_large_150_by_150():
    rng = random.Random(4700)
    g = [[rng.randint(-10**6, 10**6) for _ in range(150)] for _ in range(150)]
    want = by_column_pairs(g)
    got = ask(g, timeout=10)
    assert got == [str(want)], (
        f"150 x 150 grid: expected {want}, got {got}. If it timed out, you are trying all rectangles one by one "
        "(about 130 million). Fix two rows and run Kadane on the column sums: O(r^2 c).")


def test_large_wide():
    rng = random.Random(4701)
    g = [[rng.randint(-50, 60) for _ in range(100)] for _ in range(30)]
    want = by_column_pairs(g)
    got = ask(g, timeout=8)
    assert got == [str(want)], f"30 x 100 grid: expected {want}, got {got}. Rows and columns may differ in number."
