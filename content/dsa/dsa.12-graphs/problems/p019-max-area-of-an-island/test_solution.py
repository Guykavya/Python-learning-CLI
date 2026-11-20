import random

from solution import max_area


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
    sizes = {}
    for root in label.values():
        sizes[root] = sizes.get(root, 0) + 1
    return max(sizes.values(), default=0)


def test_the_examples():
    sea = ["11000", "11010", "00011", "10000"]
    got = max_area(sea)
    assert got == 4, f"The islands have areas 4, 3 and 1: the answer is 4, got {got}. (If you got 3, you counted islands.)"
    try:
        assert max_area(["000"]) == 0, "No land: area 0."
        assert max_area([]) == 0, "An empty map: 0."
    except (ValueError, IndexError) as e:
        raise AssertionError(f"A map without land crashed ({type(e).__name__}: {e}). max() of an empty list fails: start from 0 or use max(..., default=0), and check `if not grid`.") from None


def test_cells_are_not_counted_twice():
    got = max_area(["11", "11"])
    assert got == 4, (
        f"A 2 x 2 block has area 4, got {got}. If you got more, cells reachable from two neighbours were pushed and counted twice: "
        "mark a cell as seen when you PUSH it.")
    got = max_area(["111", "101", "111"])
    assert got == 8, f"A ring of 8 cells around a water cell: area 8, got {got}."


def test_diagonals_do_not_join():
    assert max_area(["10", "01"]) == 1, "Diagonal cells are separate islands of area 1 each."


def test_random_maps():
    rng = random.Random(1219)
    for _ in range(300):
        rows, cols = rng.randint(1, 7), rng.randint(1, 7)
        grid = ["".join(rng.choice("0111") for _ in range(cols)) for _ in range(rows)]
        want = model(grid)
        got = max_area(grid)
        assert got == want, f"max_area({grid}) should be {want}, got {got}."


def test_all_land():
    grid = ["1" * 300] * 300
    try:
        got = max_area(grid)
    except RecursionError:
        raise AssertionError("RecursionError on a 300 x 300 map of land: use an iterative DFS (an explicit stack) or BFS.") from None
    assert got == 90_000, f"A 300 x 300 map of land is one island of area 90,000, got {got}."
    assert grid[0] == "1" * 300, "Do not change the caller's map."
