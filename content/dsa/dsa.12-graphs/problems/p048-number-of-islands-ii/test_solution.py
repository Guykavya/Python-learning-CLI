import pathlib
import random
import subprocess
import sys

from solution import islands_after_each

HERE = pathlib.Path(__file__).parent


def count_islands(rows, cols, land):
    seen, count = set(), 0
    for cell in land:
        if cell in seen:
            continue
        count += 1
        seen.add(cell)
        stack = [cell]
        while stack:
            r, c = stack.pop()
            for nb in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if nb in land and nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
    return count


def brute(rows, cols, positions):
    land, out = set(), []
    for p in positions:
        land.add(tuple(p))
        out.append(count_islands(rows, cols, land))
    return out


def test_examples():
    assert islands_after_each(3, 3, [(0, 0), (0, 1), (1, 2), (2, 1), (1, 1)]) == [1, 1, 2, 3, 1], (
        "The last cell (1,1) joins three islands into one: 3 + 1 - 3 = 1.")
    assert islands_after_each(1, 2, [(0, 0), (0, 0), (0, 1)]) == [1, 1, 1], (
        "A repeated position changes nothing: do not count the same cell as a new island.")
    assert islands_after_each(2, 2, [(0, 1), (1, 0)]) == [1, 2], (
        "Diagonal cells are separate islands (4 directions only). In the flat numbering (0,1) and (1,0) are 1 and 2: "
        "find neighbours from (r, c) with bounds checks, not as i - 1 / i + 1.")


def test_same_island_from_two_sides():
    got = islands_after_each(2, 2, [(0, 0), (0, 1), (1, 0), (1, 1)])
    assert got == [1, 1, 1, 1], (
        f"Expected [1, 1, 1, 1], got {got}. The last cell (1,1) touches the SAME island from above and from the left: "
        "the count goes down only once. Use the True/False result of union.")


def test_row_wrap_is_not_a_neighbour():
    got = islands_after_each(3, 3, [(0, 2), (1, 0)])
    assert got == [1, 2], (
        f"Expected [1, 2], got {got}. (0,2) is the last cell of row 0 and (1,0) the first of row 1: neighbours in "
        "the flat numbering (2 and 3), but not on the map. Check the column bounds.")
    got = islands_after_each(2, 3, [(1, 0), (0, 2)])
    assert got == [1, 2], f"(1,0) and (0,2) do not touch; expected [1, 2], got {got}."


def test_random_against_brute_force():
    rng = random.Random(48)
    for _ in range(200):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        positions = [(rng.randrange(rows), rng.randrange(cols)) for _ in range(rng.randint(1, 25))]
        expected = brute(rows, cols, positions)
        assert islands_after_each(rows, cols, positions) == expected, (
            f"rows={rows}, cols={cols}, positions={positions}: expected {expected}.")


def test_big_map_time_limit():
    code = (
        "import random\n"
        "from solution import islands_after_each\n"
        "rng = random.Random(7)\n"
        "rows = cols = 300\n"
        "pos = [(rng.randrange(rows), rng.randrange(cols)) for _ in range(100000)]\n"
        "out = islands_after_each(rows, cols, pos)\n"
        "print(len(out), out[-1], max(out))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=15, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (15 s): 100,000 steps on a 300 x 300 map. A flood fill after every step is 9 billion cell "
        "visits; keep the count up to date with Union-Find instead.")
    assert "RecursionError" not in r.stderr, "RecursionError: write find with loops."
    assert r.returncode == 0, "Your code crashed on the big map:\n" + r.stderr[-800:]
    parts = r.stdout.split()
    assert parts and parts[0] == "100000", f"Return one count per position (100,000), got {r.stdout.strip()!r}."
    assert parts == EXPECTED_BIG, f"Big map: expected {EXPECTED_BIG}, got {parts}."


EXPECTED_BIG = ["100000", "990", "11670"]          # checked against a flood fill of the final map
