import pathlib
import random
import subprocess
import sys

from solution import Fenwick2D

HERE = pathlib.Path(__file__).parent


def test_example():
    f = Fenwick2D(3, 4)
    grid = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
    for r in range(3):
        for c in range(4):
            f.add(r, c, grid[r][c])
    assert (f.rect(0, 0, 3, 4), f.rect(1, 1, 3, 3), f.rect(0, 0, 1, 4), f.rect(2, 2, 2, 4)) == (78, 34, 10, 0)
    f.add(1, 2, 100)
    assert (f.rect(1, 1, 3, 3), f.rect(1, 2, 2, 3)) == (134, 107)


def test_non_square():
    f = Fenwick2D(2, 7)
    f.add(1, 6, 5)
    f.add(0, 0, 1)
    assert f.rect(0, 0, 2, 7) == 6 and f.rect(1, 6, 2, 7) == 5 and f.rect(0, 1, 2, 7) == 5, (
        "Rows and columns have different sizes: bound the row loop by rows and the column loop by cols.")


def test_random_against_grid():
    rng = random.Random(1622)
    for _ in range(40):
        R, C = rng.randint(1, 8), rng.randint(1, 8)
        g = [[0] * C for _ in range(R)]
        f = Fenwick2D(R, C)
        for step in range(50):
            r, c, v = rng.randrange(R), rng.randrange(C), rng.randint(-9, 9)
            g[r][c] += v
            f.add(r, c, v)
            r1, r2 = sorted((rng.randint(0, R), rng.randint(0, R)))
            c1, c2 = sorted((rng.randint(0, C), rng.randint(0, C)))
            want = sum(g[i][j] for i in range(r1, r2) for j in range(c1, c2))
            assert f.rect(r1, c1, r2, c2) == want, f"{R}x{C} grid: rect({r1}, {c1}, {r2}, {c2}) should be {want}."


BIG_CODE = (
    "import random\n"
    "from solution import Fenwick2D\n"
    "rng = random.Random(1622)\n"
    "R, C = 300, 300\n"
    "f = Fenwick2D(R, C)\n"
    "x = 0\n"
    "for _ in range(10**5):\n"
    "    if rng.random() < 0.5:\n"
    "        f.add(rng.randrange(R), rng.randrange(C), rng.randint(-10**6, 10**6))\n"
    "    else:\n"
    "        x ^= f.rect(rng.randint(0, 30), rng.randint(0, 30), rng.randint(270, R), rng.randint(270, C))\n"
    "print(x)\n"
)
BIG_WANT = ['519622709']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=60, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, ("too slow: each rectangle must take O(log rows * log cols) steps; adding up 70,000 shelves per question is too much.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
