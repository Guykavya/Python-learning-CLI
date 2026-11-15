import random

import pytest

from solution import minutes_to_rot


def simulate(grid):
    """Minute-by-minute simulation, no queue."""
    g = [row[:] for row in grid]
    minutes = 0
    while True:
        fresh = sum(row.count(1) for row in g)
        if fresh == 0:
            return minutes
        new = [row[:] for row in g]
        for r in range(len(g)):
            for c in range(len(g[0])):
                if g[r][c] == 1 and any(0 <= r + dr < len(g) and 0 <= c + dc < len(g[0]) and g[r + dr][c + dc] == 2
                                        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    new[r][c] = 2
        if new == g:
            return -1
        g = new
        minutes += 1


@pytest.mark.parametrize("grid, want, why", [
    ([[2, 1, 1], [1, 1, 0], [0, 1, 1]], 4, "the classic example"),
    ([[2, 1, 1], [0, 1, 1], [1, 0, 1]], -1, "the bottom-left orange is cut off by empty cells"),
    ([[0, 2]], 0, "no fresh orange at all: 0 minutes"),
    ([], 0, "an empty grid"),
    ([[0, 0]], 0, "nothing at all"),
    ([[1]], -1, "a fresh orange and no rotten one"),
    ([[2, 1, 1, 1, 2]], 2, "two sources spread AT THE SAME TIME: put all rotten oranges in the queue first"),
    ([[2], [1], [1], [1]], 3, "a column"),
    ([[1, 1], [1, 2]], 2, "the far corner needs two minutes"),
])
def test_cases(grid, want, why):
    got = minutes_to_rot([row[:] for row in grid])
    assert got == want, f"minutes_to_rot({grid}) should be {want}, got {got}: {why}."


def test_random_against_simulation():
    rng = random.Random(39)
    for _ in range(500):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        grid = [[rng.choice([0, 1, 1, 1, 2]) for _ in range(cols)] for _ in range(rows)]
        want = simulate(grid)
        got = minutes_to_rot([row[:] for row in grid])
        assert got == want, f"minutes_to_rot({grid}) should be {want}, got {got}."


def test_big_grid():
    grid = [[1] * 200 for _ in range(200)]
    grid[0][0] = 2
    grid[199][199] = 2
    assert minutes_to_rot(grid) == 199, (
        "200 x 200 fresh oranges with rotten ones in two opposite corners: the cells on the middle diagonal "
        "are 199 steps from both corners.")
