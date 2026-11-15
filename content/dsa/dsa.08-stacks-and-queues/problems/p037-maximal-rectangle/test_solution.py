import random

import pytest

from solution import histograms, maximal_rectangle

EXAMPLE = ["10100",
           "10111",
           "11111",
           "10010"]

# Hand-traced, then confirmed by running: the heights of each row of EXAMPLE.
EXAMPLE_HEIGHTS = [[1, 0, 1, 0, 0],
                   [2, 0, 2, 1, 1],
                   [3, 1, 3, 2, 2],
                   [4, 0, 0, 3, 0]]


def slow(grid):
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])
    best = 0
    for top in range(rows):
        ok = [True] * cols
        for bottom in range(top, rows):
            ok = [ok[c] and grid[bottom][c] == "1" for c in range(cols)]
            run = 0
            for c in range(cols):
                run = run + 1 if ok[c] else 0
                best = max(best, run * (bottom - top + 1))
    return best


def test_example_histograms():
    got = histograms(EXAMPLE)
    assert len(got) == 4, f"There must be one list of heights per row (4), got {len(got)}."
    for r in range(4):
        assert got[r] == EXAMPLE_HEIGHTS[r], (
            f"Row {r} ({EXAMPLE[r]!r}): the heights should be {EXAMPLE_HEIGHTS[r]}, got {got[r]}. "
            "A '1' adds one to the height above it; a '0' resets the column to 0. "
            "If every row looks the same, you appended the same list object each time.")


def test_example_area():
    assert maximal_rectangle(EXAMPLE) == 6, (
        "The example's best rectangle is 2 high and 3 wide (rows 1-2, columns 2-4): area 6.")


@pytest.mark.parametrize("grid, want, why", [
    ([], 0, "an empty grid"),
    (["", ""], 0, "rows without columns"),
    (["0"], 0, "a single 0"),
    (["1"], 1, "a single 1"),
    (["111", "111"], 6, "all ones: the whole grid"),
    (["000", "000"], 0, "all zeros"),
    (["101", "111", "101"], 3, "a plus shape: a full row or a full column, area 3"),
    (["0110", "0110", "1111"], 6, "a 3x2 block in the middle columns"),
    (["1", "1", "0", "1"], 2, "a column with a gap: the 0 resets the height"),
])
def test_cases(grid, want, why):
    got = maximal_rectangle(list(grid))
    assert got == want, f"maximal_rectangle({grid}) should be {want}, got {got}: {why}."


def test_random_against_slow():
    rng = random.Random(37)
    for _ in range(400):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        p = rng.choice([0.5, 0.7, 0.9])
        grid = ["".join("1" if rng.random() < p else "0" for _ in range(cols)) for _ in range(rows)]
        assert maximal_rectangle(grid) == slow(grid), f"maximal_rectangle({grid}) should be {slow(grid)}."


def test_big():
    grid = ["1" * 200] * 200
    assert maximal_rectangle(grid) == 40000, "A 200 x 200 grid of ones has area 40,000."
