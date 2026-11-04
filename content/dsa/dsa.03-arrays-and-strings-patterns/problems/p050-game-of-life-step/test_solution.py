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


def ask(rows, k, timeout=10):
    return run(f"{len(rows)} {len(rows[0])} {k}\n" + "\n".join(rows) + "\n", timeout=timeout)


def by_live_set(rows, k):
    """Independent check: keep only the set of live cells and count neighbours with a dictionary."""
    r, c = len(rows), len(rows[0])
    live = {(i, j) for i in range(r) for j in range(c) if rows[i][j] == "#"}
    for _ in range(k):
        counts = {}
        for (i, j) in live:
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if (di or dj) and 0 <= i + di < r and 0 <= j + dj < c:
                        counts[(i + di, j + dj)] = counts.get((i + di, j + dj), 0) + 1
        live = {p for p, n in counts.items() if n == 3 or (n == 2 and p in live)}
    return ["".join("#" if (i, j) in live else "." for j in range(c)) for i in range(r)]


def show(rows):
    return "\n" + "\n".join(rows) + "\n"


BLINKER = [".....", ".....", ".###.", ".....", "....."]
BLINKER_V = [".....", "..#..", "..#..", "..#..", "....."]


def test_example_blinker():
    got = ask(BLINKER, 1)
    assert got == BLINKER_V, (
        f"Expected{show(BLINKER_V)}got{show(got)}If the result is lopsided, you update cells in place: a cell "
        "you already changed is then counted as a neighbour. Build a new grid from the old one.")


def test_blinker_period_two():
    got = ask(BLINKER, 2)
    assert got == BLINKER, f"After 2 generations the blinker is back to a row. Got{show(got)}"


def test_k_zero():
    rows = ["#..", ".#.", "..#"]
    assert ask(rows, 0) == rows, "With k = 0 no generation runs: print the grid as it was."


def test_block_still_life():
    rows = ["....", ".##.", ".##.", "...."]
    assert ask(rows, 3) == rows, (
        "A 2 x 2 block never changes: each cell has exactly 3 alive neighbours, and no dead cell has 3.")


def test_edges_are_dead_not_wrapped():
    rows = ["###", "...", "..."]
    want = [".#.", ".#.", "..."]
    got = ask(rows, 1)
    assert got == want, (
        f"Expected{show(want)}got{show(got)}Cells outside the grid are dead: the grid does NOT wrap around. "
        "If the bottom row came alive, your neighbour index wrapped (Python's index -1 or a % r).")


def test_negative_index_trap():
    rows = ["#..", "...", "#.#"]
    want = ["...", ".#.", "..."]
    got = ask(rows, 1)
    assert got == want, (
        f"Expected{show(want)}got{show(got)}Check the bounds 0 <= ni < r and 0 <= nj < c before reading "
        "grid[ni][nj]. In Python grid[-1] is the LAST row, so a missing check silently wraps around.")


def test_overcrowding():
    rows = ["###", "###", "###"]
    want = ["#.#", "...", "#.#"]
    got = ask(rows, 1)
    assert got == want, (
        f"Expected{show(want)}got{show(got)}Corners have 3 alive neighbours and survive; edge cells have 5 and "
        "the centre has 8: they die of overcrowding. Count all 8 directions, and do not count the cell itself.")


def test_single_cell():
    assert ask(["#"], 1) == ["."], "A lone cell has 0 neighbours and dies."


def test_one_row():
    got = ask([".###."], 1)
    assert got == ["..#.."], f"In a single row only left and right neighbours exist. Expected ..#.., got {got}."


def test_glider_moves():
    rows = [".#....", "..#...", "###...", "......", "......", "......"]
    want = ["......", "..#...", "...#..", ".###..", "......", "......"]
    got = ask(rows, 4)
    assert got == want, (
        f"A glider moves one cell down and one right every 4 generations. Expected{show(want)}got{show(got)}")


def test_glider_hits_corner():
    rows = [".#...", "..#..", "###..", ".....", "....."]
    want = by_live_set(rows, 10)
    got = ask(rows, 10)
    assert got == want, (
        f"A glider running into the bottom-right corner (edges dead). Expected{show(want)}got{show(got)}")


def test_random_grids():
    rng = random.Random(50)
    for _ in range(5):
        r, c = rng.randint(1, 30), rng.randint(1, 40)
        rows = ["".join(rng.choice("#..") for _ in range(c)) for _ in range(r)]
        k = rng.randint(1, 10)
        got = ask(rows, k)
        want = by_live_set(rows, k)
        assert got == want, f"Random {r} x {c} grid, k = {k}: the output differs from the expected grid."


def test_largest_grid():
    rng = random.Random(5000)
    rows = ["".join(rng.choice("#..") for _ in range(100)) for _ in range(100)]
    got = ask(rows, 10, timeout=10)
    assert got == by_live_set(rows, 10), "A 100 x 100 grid after 10 generations differs from the expected grid."
