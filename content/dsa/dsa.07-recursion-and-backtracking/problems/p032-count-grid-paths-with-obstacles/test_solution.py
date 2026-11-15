import random

import pytest

from solution import count_paths


def brute(grid):
    """Independent count: grow paths as tuples of cells (no shared state)."""
    R, C = len(grid), len(grid[0])
    if grid[0][0] == "#" or grid[R - 1][C - 1] == "#":
        return 0
    count = 0
    stack = [((0, 0),)]
    while stack:
        path = stack.pop()
        r, c = path[-1]
        if (r, c) == (R - 1, C - 1):
            count += 1
            continue
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == "." and (nr, nc) not in path:
                stack.append(path + ((nr, nc),))
    return count


@pytest.mark.parametrize("grid, want, why", [
    (["."], 1, "a 1x1 free grid: you are already at the end"),
    (["..", ".."], 2, "right-down or down-right"),
    (["...", "...", "..."], 12, "the 3x3 open grid has 12 self-avoiding paths (chapter section 10)"),
    (["....", "....", "....", "...."], 184, "the 4x4 open grid has 184 paths"),
    ([".#", ".."], 1, "only down then right"),
    (["#.", ".."], 0, "the start is a wall"),
    ([".", "#", "."], 0, "the wall cuts the only route"),
    (["...."], 1, "a single row: one straight path"),
    ([".#.", "...", ".#."], 1, "a plus-shaped grid: only one route through the middle"),
])
def test_cases(grid, want, why):
    got = count_paths(list(grid))
    assert got == want, (
        f"count_paths({grid}) should be {want} ({why}), got {got}. "
        "Too small: did you forget to un-mark the cell? Too big: do you mark it before visiting the neighbours?")


def test_called_twice():
    g = ["...", "...", "..."]
    a = count_paths(g)
    b = count_paths(g)
    assert a == b == 12, "Two calls must give the same answer: do not keep visited marks between calls."


def test_random_against_brute_force():
    rng = random.Random(32)
    for _ in range(60):
        R, C = rng.randint(1, 4), rng.randint(1, 4)
        grid = ["".join("#" if rng.random() < 0.25 else "." for _ in range(C)) for _ in range(R)]
        want = brute(grid)
        assert count_paths(grid) == want, f"count_paths({grid}) should be {want}."


def test_five_by_five():
    grid = ["..#..", ".....", "#.#.#", ".....", "..#.."]
    want = brute(grid)
    assert count_paths(grid) == want, f"count_paths({grid}) should be {want}."
