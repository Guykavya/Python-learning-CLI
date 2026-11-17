import random

from solution import neighbours

GRID = ["..#.",
        ".##.",
        "...."]


def model(grid, r, c, diagonal):
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if diagonal:
        moves += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    out = []
    for dr, dc in moves:
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != "#":
            out.append((nr, nc))
    return out


def as_pairs(cells):
    return [tuple(x) for x in cells]


def test_the_examples():
    assert as_pairs(neighbours(GRID, 0, 0)) == [(1, 0), (0, 1)], "(0, 0): down (1, 0) then right (0, 1). Up and left are outside the grid."
    assert as_pairs(neighbours(GRID, 2, 1)) == [(2, 0), (2, 2)], "(2, 1): up is a wall, down is outside; left (2, 0), right (2, 2)."
    assert as_pairs(neighbours(GRID, 2, 1, diagonal=True)) == [(2, 0), (2, 2), (1, 0)], (
        "With diagonals: the straight moves first, then up-left (1, 0); up-right (1, 2) is a wall.")


def test_no_wrap_around():
    got = as_pairs(neighbours(["...", "...", "..."], 0, 0, diagonal=True))
    assert got == [(1, 0), (0, 1), (1, 1)], (
        f"Corner (0, 0) with diagonals has only 3 neighbours, got {got}. Negative indexes wrap around in Python "
        "(grid[-1] is the last row): check 0 <= nr and 0 <= nc before looking at the cell.")
    got = as_pairs(neighbours(["...", "...", "..."], 2, 2))
    assert got == [(1, 2), (2, 1)], f"Corner (2, 2): only up and left; got {got}."


def test_one_cell_and_walls():
    assert as_pairs(neighbours(["."], 0, 0, diagonal=True)) == [], "A 1x1 grid has no neighbours."
    assert as_pairs(neighbours(["#.#", "...", "#.#"], 1, 1)) == [(0, 1), (2, 1), (1, 0), (1, 2)], "The centre of a plus: up, down, left, right."
    assert as_pairs(neighbours(["#.#", "...", "#.#"], 1, 1, diagonal=True)) == [(0, 1), (2, 1), (1, 0), (1, 2)], "The four diagonal cells are walls."
    assert as_pairs(neighbours(["#.", ".."], 0, 0)) == [(1, 0), (0, 1)], "The cell itself may be a wall: only the neighbours are checked."


def test_random_grids():
    rng = random.Random(1205)
    for _ in range(200):
        rows, cols = rng.randint(1, 5), rng.randint(1, 5)
        grid = ["".join(rng.choice(".#") for _ in range(cols)) for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                for diagonal in (False, True):
                    want = model(grid, r, c, diagonal)
                    got = as_pairs(neighbours(grid, r, c, diagonal))
                    assert got == want, f"neighbours({grid}, {r}, {c}, diagonal={diagonal}) should be {want}, got {got}."
