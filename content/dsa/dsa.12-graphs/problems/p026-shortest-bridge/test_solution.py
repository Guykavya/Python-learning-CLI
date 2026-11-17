import pathlib
import random
import subprocess
import sys

from solution import shortest_bridge

HERE = pathlib.Path(__file__).parent
STEPS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def islands(grid):
    rows, cols = len(grid), len(grid[0])
    seen, result = set(), []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in seen:
                seen.add((r, c))
                stack, cells = [(r, c)], []
                while stack:
                    a, b = stack.pop()
                    cells.append((a, b))
                    for dr, dc in STEPS:
                        na, nb = a + dr, b + dc
                        if 0 <= na < rows and 0 <= nb < cols and grid[na][nb] == "1" and (na, nb) not in seen:
                            seen.add((na, nb))
                            stack.append((na, nb))
                result.append(cells)
    return result


def brute(grid):
    one, two = islands(grid)
    return min(abs(a - c) + abs(b - d) for a, b in one for c, d in two) - 1


def test_examples():
    assert shortest_bridge(["010", "000", "001"]) == 2, (
        "Islands at (0,1) and (2,2): two water cells must be flipped. If you got 3, you returned the distance "
        "of the land cell you reached instead of the number of water cells in between.")
    assert shortest_bridge(["11000", "10001", "00011"]) == 3, (
        "The example with two L-shaped islands needs 3 flips: the nearest cells, (0,1) and (1,4), are 1 + 3 = 4 "
        "steps apart, so 3 water cells lie between them.")
    assert shortest_bridge(["101"]) == 1, "One water cell between the islands: 1 flip."


def test_diagonal_islands_need_one_flip():
    assert shortest_bridge(["10", "01"]) == 1, (
        "Two cells that touch only at a corner are TWO islands (only up/down/left/right count), and one flip joins them.")


def test_nearest_edge_not_one_cell():
    grid = ["1111111110",
            "0000000000",
            "0000000000",
            "0000000001"]
    assert shortest_bridge(grid) == 3, (
        "The nearest cells are (0,8) and (3,9): |0-3| + |8-9| - 1 = 3 flips. If you got 11, your BFS started "
        "only from (0,0): start it from EVERY cell of the first island at once (multi-source BFS).")


def test_random_grids_against_brute_force():
    rng = random.Random(26)
    checked = 0
    while checked < 300:
        rows, cols = rng.randint(1, 8), rng.randint(1, 8)
        grid = ["".join("1" if rng.random() < 0.3 else "0" for _ in range(cols)) for _ in range(rows)]
        if len(islands(grid)) != 2:
            continue
        checked += 1
        assert shortest_bridge(grid) == brute(grid), (
            f"Grid {grid}: expected {brute(grid)} flips. Check: 4 directions only, multi-source BFS from the whole "
            "first island, and return the number of WATER cells crossed.")


def run_limited(code, timeout):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None
    return r


def test_big_islands_with_time_limit():
    code = (
        "import sys\n"
        "sys.setrecursionlimit(1000)\n"
        "from solution import shortest_bridge\n"
        "n = 300\n"
        "grid = ['1' * 100 + '0' * 100 + '1' * 100 for _ in range(n)]\n"
        "print(shortest_bridge(grid))\n"
    )
    r = run_limited(code, 10)
    assert r is not None, (
        "Time limit (10 s) on a 300 x 300 grid with two islands of 30,000 cells each. Comparing every pair of cells "
        "is 900 million pairs: use one flood fill and one multi-source BFS, O(rows * cols).")
    assert "RecursionError" not in r.stderr, (
        "RecursionError on an island of 30,000 cells: flood-fill with an explicit stack, not recursion.")
    assert r.returncode == 0, "Your code crashed on the big grid:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["100"], f"The big grid needs 100 flips (columns 100..199), you printed {r.stdout.strip()!r}."


def test_snake_island_no_recursion():
    code = (
        "from solution import shortest_bridge\n"
        "rows, cols = 201, 200\n"
        "g = [['0'] * cols for _ in range(rows)]\n"
        "for r in range(0, 199, 2):\n"
        "    for c in range(cols):\n"
        "        g[r][c] = '1'\n"
        "    g[r + 1][cols - 1 if (r // 2) % 2 == 0 else 0] = '1'\n"
        "g[199] = ['0'] * cols\n"
        "g[200] = ['0'] * (cols - 1) + ['1']\n"
        "g[198][cols - 1] = '1'\n"
        "print(shortest_bridge([''.join(row) for row in g]))\n"
    )
    r = run_limited(code, 15)
    assert r is not None, "Time limit on a snake-shaped island of about 20,000 cells."
    assert "RecursionError" not in r.stderr, (
        "RecursionError on a snake-shaped island: a recursive flood fill makes one nested call per cell. Use a stack.")
    assert r.returncode == 0, "Your code crashed on the snake grid:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["1"], f"The snake grid needs 1 flip, you printed {r.stdout.strip()!r}."
