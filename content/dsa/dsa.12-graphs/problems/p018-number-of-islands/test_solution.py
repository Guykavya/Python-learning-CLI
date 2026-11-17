import random

from solution import num_islands


def model(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    label = {}
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                label[(r, c)] = (r, c)
    changed = True
    while changed:
        changed = False
        for (r, c) in label:
            for nb in ((r + 1, c), (r, c + 1)):
                if nb in label and label[nb] != label[(r, c)]:
                    m = min(label[nb], label[(r, c)])
                    label[nb] = label[(r, c)] = m
                    changed = True
    return len(set(label.values()))


def test_a_empty_first():
    test_small_maps()


def test_the_examples():
    sea = ["11000", "11010", "00011", "10000"]
    assert num_islands(sea) == 3, "Three islands: the 2x2 block, the group around (1, 3), and the single cell (3, 0)."
    assert num_islands(["101", "010", "101"]) == 5, "Cells that touch only at a corner are NOT joined: five islands. Use 4 directions, not 8."


def test_small_maps():
    try:
        got = num_islands([])
    except IndexError:
        raise AssertionError("num_islands([]) crashed with IndexError: an empty map has no row, so check `if not grid` before len(grid[0]).") from None
    assert got == 0, "An empty map has no islands."
    assert num_islands(["1"]) == 1, "A single land cell is one island."
    assert num_islands(["0"]) == 0, "A single water cell: no island."
    assert num_islands(["000", "000"]) == 0, "All water: no island."
    assert num_islands(["111"]) == 1, "One row of land: one island, not three (count islands, not land cells)."


def test_top_and_bottom_rows_are_not_neighbours():
    assert num_islands(["1", "0", "1"]) == 2, (
        "Land at the top and at the bottom are two islands. If you got 1, a negative index wrapped around (grid[-1] is the last row): "
        "check 0 <= nr before looking at the cell.")
    assert num_islands(["101"]) == 2, "Land at the left and right ends: two islands (check 0 <= nc)."


def test_grid_is_not_changed():
    g = ["110", "011"]
    before = list(g)
    num_islands(g)
    assert g == before, "num_islands changed the caller's list: work on a copy if you want to sink land."


def test_random_maps():
    rng = random.Random(1218)
    for _ in range(300):
        rows, cols = rng.randint(1, 7), rng.randint(1, 7)
        grid = ["".join(rng.choice("0011") for _ in range(cols)) for _ in range(rows)]
        want = model(grid)
        got = num_islands(grid)
        assert got == want, f"num_islands({grid}) should be {want}, got {got}."


def test_all_land_is_one_island():
    for size in (100, 300):
        grid = ["1" * size] * size
        try:
            got = num_islands(grid)
        except RecursionError:
            raise AssertionError(f"RecursionError on a {size} x {size} map of land: use an iterative DFS (an explicit stack) or BFS.") from None
        assert got == 1, f"A {size} x {size} map of land is one island, got {got}."


def test_chessboard():
    grid = ["".join("1" if (r + c) % 2 == 0 else "0" for c in range(60)) for r in range(60)]
    assert num_islands(grid) == 1800, "A 60 x 60 chessboard of land and water has 1,800 single-cell islands."
