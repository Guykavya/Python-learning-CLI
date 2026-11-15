import random

import pytest

from solution import count_islands


def union_find_count(grid):
    R, C = len(grid), len(grid[0])
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for r in range(R):
        for c in range(C):
            if grid[r][c] == "#":
                parent[(r, c)] = (r, c)
    for r in range(R):
        for c in range(C):
            if grid[r][c] == "#":
                for nr, nc in ((r + 1, c), (r, c + 1)):
                    if nr < R and nc < C and grid[nr][nc] == "#":
                        parent[find((r, c))] = find((nr, nc))
    return len({find(x) for x in parent})


@pytest.mark.parametrize("grid, want, why", [
    (["##..", "#...", "..##", "...#"], 2, "the example"),
    (["#.#", ".#."], 3, "diagonal neighbours do not connect"),
    (["#"], 1, "a 1x1 island"),
    (["."], 0, "a 1x1 grid of water"),
    (["...", "..."], 0, "no land at all"),
    (["###", "#.#", "###"], 1, "a ring is one island"),
    (["#.#.#.#"], 4, "a row of separate cells"),
])
def test_cases(grid, want, why):
    got = count_islands(list(grid))
    assert got == want, f"count_islands({grid}) should be {want} ({why}), got {got}."


def test_long_strip():
    grid = ["#"] * 150
    assert count_islands(grid) == 1, "A 150x1 strip of land is one island (a recursive fill goes 150 deep here, which is fine)."


def test_random_against_union_find():
    rng = random.Random(33)
    for _ in range(80):
        R, C = rng.randint(1, 8), rng.randint(1, 8)
        grid = ["".join("#" if rng.random() < 0.45 else "." for _ in range(C)) for _ in range(R)]
        want = union_find_count(grid)
        assert count_islands(grid) == want, f"count_islands({grid}) should be {want}."


def snake(n):
    rows = []
    for r in range(n):
        if r % 2 == 0:
            rows.append("#" * n)
        elif r % 4 == 1:
            rows.append("." * (n - 1) + "#")
        else:
            rows.append("#" + "." * (n - 1))
    return rows


def test_snake_island_needs_explicit_stack():
    grid = snake(49)
    cells = sum(row.count("#") for row in grid)
    assert cells > 1200
    try:
        got = count_islands(grid)
    except RecursionError:
        raise AssertionError(
            f"RecursionError on a snake-shaped island of {cells} cells: a recursive flood fill goes deeper than "
            "Python's limit of about 1000 calls. Rewrite the fill with an explicit stack (a list you push and pop).") from None
    assert got == 1, f"The snake is one island of {cells} cells, got {got}."


def test_big_grid_many_islands():
    grid = ["#." * 30, ".#" * 30] * 30
    assert count_islands(grid) == 1800, "A 60x60 checkerboard: every land cell is its own island (1800 islands)."
