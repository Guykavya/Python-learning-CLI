import pathlib
import random
import subprocess
import sys

from solution import pacific_atlantic

HERE = pathlib.Path(__file__).parent


def run_limited(code, seconds):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=seconds, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None
    return r


def brute(h):
    rows = len(h)
    cols = len(h[0]) if rows else 0
    out = []
    for r in range(rows):
        for c in range(cols):
            seen, stack = {(r, c)}, [(r, c)]
            pac = atl = False
            while stack:
                a, b = stack.pop()
                if a == 0 or b == 0:
                    pac = True
                if a == rows - 1 or b == cols - 1:
                    atl = True
                for x, y in ((a - 1, b), (a + 1, b), (a, b - 1), (a, b + 1)):
                    if 0 <= x < rows and 0 <= y < cols and (x, y) not in seen and h[x][y] <= h[a][b]:
                        seen.add((x, y))
                        stack.append((x, y))
            if pac and atl:
                out.append((r, c))
    return out


EXAMPLE = [[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]


def norm(cells):
    return [tuple(x) for x in cells]


def test_the_example():
    got = norm(pacific_atlantic(EXAMPLE))
    want = [(0, 4), (1, 3), (1, 4), (2, 2), (3, 0), (3, 1), (4, 0)]
    assert got == want, f"Expected {want}, got {got}. Return sorted (r, c) tuples."


def test_level_ground_flows():
    got = norm(pacific_atlantic([[1, 1], [1, 1]]))
    assert got == [(0, 0), (0, 1), (1, 0), (1, 1)], (
        f"On level ground water flows everywhere (height <= its own): every cell reaches both oceans. Got {got}. "
        "In the reverse search allow EQUAL heights (>=, not >).")


def test_direction_of_the_reverse_search():
    h = [[3, 3, 3], [3, 1, 3], [3, 3, 3]]
    got = norm(pacific_atlantic(h))
    want = brute(h)
    assert got == want, (
        f"The pit (1, 1) of height 1 cannot send water anywhere higher: expected {want}, got {got}. "
        "Walking back from the ocean, you may only step to a neighbour that is HIGHER or LEVEL.")


def test_small_grids():
    assert norm(pacific_atlantic([])) == [], "An empty grid gives []."
    assert norm(pacific_atlantic([[7]])) == [(0, 0)], "A 1x1 island touches all four edges."
    assert norm(pacific_atlantic([[1, 2, 3]])) == [(0, 0), (0, 1), (0, 2)], (
        "A single row: every cell is on the top edge (Pacific) and on the bottom edge (Atlantic).")
    got = norm(pacific_atlantic([[1], [2], [0]]))
    assert got == [(0, 0), (1, 0), (2, 0)], f"A single column touches the left and right edges: all cells, got {got}."


def test_random_grids_against_brute_force():
    rng = random.Random(1222)
    for _ in range(300):
        rows, cols = rng.randint(1, 7), rng.randint(1, 7)
        h = [[rng.randint(0, 4) for _ in range(cols)] for _ in range(rows)]
        want = brute(h)
        got = norm(pacific_atlantic(h))
        assert got == want, f"pacific_atlantic({h}) should be {want}, got {got}."


def test_big_grid_is_fast():
    code = (
        "import random\n"
        "from solution import pacific_atlantic\n"
        "rng = random.Random(7)\n"
        "h = [[rng.randint(0, 100000) for _ in range(300)] for _ in range(300)]\n"
        "a = pacific_atlantic(h)\n"
        "flat = [[50] * 300 for _ in range(300)]\n"
        "b = pacific_atlantic(flat)\n"
        "print(len(a), len(b))\n"
    )
    r = run_limited(code, 10)
    assert r is not None, (
        "Two 300 x 300 grids took more than 10 seconds. Searching from every cell is O((rows*cols)^2): "
        "search backwards from the two coasts instead (two multi-source searches).")
    assert r.returncode == 0, "The big-grid run crashed:\n" + r.stderr[-800:]
    a, b = r.stdout.split()
    assert b == "90000", f"On a flat 300 x 300 island every cell reaches both oceans (90,000 cells), got {b}."
