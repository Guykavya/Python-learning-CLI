import random

import pytest

from solution import longest_path


def bitmask_dp(grid):
    """Independent answer: reach[mask] = set of end cells of paths that visit exactly `mask`."""
    cells = [(r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == "."]
    if not cells:
        return 0
    index = {cell: i for i, cell in enumerate(cells)}
    nbrs = []
    for r, c in cells:
        nbrs.append([index[p] for p in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)) if p in index])
    reach = {1 << i: {i} for i in range(len(cells))}
    best = 1
    frontier = list(reach)
    while frontier:
        new = {}
        for mask in frontier:
            for end in reach[mask]:
                for j in nbrs[end]:
                    if not mask >> j & 1:
                        new.setdefault(mask | 1 << j, set()).add(j)
        for m, ends in new.items():
            reach.setdefault(m, set()).update(ends)
            best = max(best, bin(m).count("1"))
        frontier = list(new)
    return best - 1


@pytest.mark.parametrize("grid, want, why", [
    (["...", "...", "..."], 8, "a snake through all 9 cells: 8 moves"),
    ([".#.", "...", ".#."], 4, "the plus shape: the best path visits 5 cells"),
    (["#"], 0, "no free cell"),
    (["."], 0, "one free cell, no move"),
    (["...."], 3, "a single row of 4 cells: start at one end"),
    (["....", "....", "....", "...."], 15, "the 4x4 open grid has a path through all 16 cells"),
    (["..", "#."], 2, "an L shape of three cells"),
    (["#.#", "...", "#.#"], 2, "a cross: at most one arm, the centre and another arm"),
])
def test_cases(grid, want, why):
    got = longest_path(list(grid))
    assert got == want, (
        f"longest_path({grid}) should be {want} ({why}), got {got}. "
        "Count moves, not cells; try every start cell; un-mark cells on the way back.")


def test_random_against_bitmask():
    rng = random.Random(34)
    for _ in range(70):
        R, C = rng.randint(1, 4), rng.randint(1, 4)
        grid = ["".join("#" if rng.random() < 0.3 else "." for _ in range(C)) for _ in range(R)]
        want = bitmask_dp(grid)
        assert longest_path(grid) == want, f"longest_path({grid}) should be {want}."
