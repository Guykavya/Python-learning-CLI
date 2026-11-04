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


def ask(r, c, updates, timeout=10):
    lines = [f"{r} {c} {len(updates)}"] + [" ".join(map(str, u)) for u in updates]
    return run("\n".join(lines) + "\n", timeout=timeout)


def brute(r, c, updates):
    g = [[0] * c for _ in range(r)]
    for r1, c1, r2, c2, v in updates:
        for i in range(r1 - 1, r2):
            for j in range(c1 - 1, c2):
                g[i][j] += v
    return [" ".join(map(str, row)) for row in g]


def test_example():
    got = ask(3, 4, [(1, 1, 2, 3, 5), (2, 2, 3, 4, -2), (3, 1, 3, 1, 7)])
    assert got == ["5 5 5 0", "5 3 3 -2", "7 -2 -2 -2"], (
        f"The example: expected rows '5 5 5 0', '5 3 3 -2', '7 -2 -2 -2'; got {got}. Check the four marks and "
        "their signs: +v, -v at column c2+1, -v at row r2+1, +v at both.")


@pytest.mark.parametrize("r, c, updates, why", [
    (1, 1, [(1, 1, 1, 1, 4)], "a 1 x 1 grid: the closing marks fall into the spare row and column"),
    (2, 3, [(1, 1, 2, 3, 1)], "an update covering the whole grid: every closing mark is outside the grid"),
    (3, 3, [(2, 2, 2, 2, 9)], "a single middle cell: only (2, 2) changes"),
    (3, 3, [(1, 3, 3, 3, 2)], "the last column: the mark at c2 + 1 needs the spare column"),
    (3, 3, [(3, 1, 3, 3, -4)], "the last row: the mark at r2 + 1 needs the spare row"),
    (2, 2, [(1, 1, 1, 1, 1), (1, 1, 1, 1, -1)], "two updates that cancel out"),
    (4, 4, [(1, 1, 3, 3, 1), (2, 2, 4, 4, 1)], "overlapping updates add up in the overlap"),
])
def test_small(r, c, updates, why):
    got = ask(r, c, updates)
    expected = brute(r, c, updates)
    assert got == expected, f"{r} x {c} grid with updates {updates}: expected {expected}, got {got} ({why})."


def test_random_small_against_brute_force():
    rng = random.Random(24)
    for _ in range(25):
        r, c = rng.randint(1, 6), rng.randint(1, 6)
        updates = []
        for _ in range(rng.randint(1, 8)):
            r1, r2 = sorted((rng.randint(1, r), rng.randint(1, r)))
            c1, c2 = sorted((rng.randint(1, c), rng.randint(1, c)))
            updates.append((r1, c1, r2, c2, rng.randint(-5, 5)))
        got = ask(r, c, updates)
        expected = brute(r, c, updates)
        assert got == expected, (
            f"{r} x {c} grid, updates {updates}: expected {expected}, got {got}. Every rectangle must change "
            "exactly its own cells, including its last row and last column.")


def test_large():
    rng = random.Random(2424)
    r = c = 400
    updates = []
    for _ in range(100000):
        r1, r2 = sorted((rng.randint(1, r), rng.randint(1, r)))
        c1, c2 = sorted((rng.randint(1, c), rng.randint(1, c)))
        updates.append((r1, c1, r2, c2, rng.randint(-10**9, 10**9)))
    # Expected values: row-by-row 1D difference arrays over the same updates, in column-sweep form.
    starts = [[] for _ in range(c + 2)]
    for r1, c1, r2, c2, v in updates:
        starts[c1].append((r1, r2, v))
        starts[c2 + 1].append((r1, r2, -v))
    col_marks = [0] * (r + 2)
    rows = [[0] * c for _ in range(r)]
    for j in range(1, c + 1):
        for r1, r2, v in starts[j]:
            col_marks[r1] += v
            col_marks[r2 + 1] -= v
        running = 0
        for i in range(1, r + 1):
            running += col_marks[i]
            rows[i - 1][j - 1] = running
    expected = [" ".join(map(str, row)) for row in rows]
    got = ask(r, c, updates, timeout=15)
    assert len(got) == r, f"Expected {r} output rows, got {len(got)}."
    bad = next((i for i in range(r) if got[i] != expected[i]), None)
    assert bad is None, (
        f"Large test: row {bad + 1} is wrong. If small tests pass but this one times out or fails, make sure each "
        "update costs O(1) (four marks) and you take the prefix sum only once at the end.")
