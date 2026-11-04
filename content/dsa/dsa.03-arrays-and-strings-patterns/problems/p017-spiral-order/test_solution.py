import subprocess
import sys
from pathlib import Path

import pytest

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import random


def ask(g, timeout=10):
    text = f"{len(g)} {len(g[0])}\n" + "".join(" ".join(map(str, row)) + "\n" for row in g)
    return run(text, timeout=timeout)


def walker(g):
    """A second algorithm: walk and turn right when blocked."""
    r, c = len(g), len(g[0])
    seen = [[False] * c for _ in range(r)]
    moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    i = j = d = 0
    out = []
    for _ in range(r * c):
        out.append(g[i][j])
        seen[i][j] = True
        ni, nj = i + moves[d][0], j + moves[d][1]
        if not (0 <= ni < r and 0 <= nj < c) or seen[ni][nj]:
            d = (d + 1) % 4
            ni, nj = i + moves[d][0], j + moves[d][1]
        i, j = ni, nj
    return [" ".join(map(str, out))]


def grid(r, c):
    return [[i * c + j + 1 for j in range(c)] for i in range(r)]


@pytest.mark.parametrize("r, c, expected, why", [
    (3, 4, "1 2 3 4 8 12 11 10 9 5 6 7", "the example: 3 x 4, the inner ring is the row 6 7"),
    (4, 3, "1 2 3 6 9 12 11 10 7 4 5 8", "4 x 3: the inner ring is the column 5 8"),
    (3, 3, "1 2 3 6 9 8 7 4 5", "3 x 3: the centre comes last"),
    (2, 2, "1 2 4 3", "2 x 2"),
    (1, 1, "1", "a single cell"),
    (1, 4, "1 2 3 4", "one row: if you print 1 2 3 4 3 2 1 you walked the same row back as the 'bottom row'. Re-check top <= bottom"),
    (4, 1, "1 2 3 4", "one column: if values repeat you walked the same column up as the 'left column'. Re-check left <= right"),
    (2, 5, "1 2 3 4 5 10 9 8 7 6", "two rows: no inner ring"),
    (5, 2, "1 2 4 6 8 10 9 7 5 3", "two columns: no inner ring"),
    (4, 4, "1 2 3 4 8 12 16 15 14 13 9 5 6 7 11 10", "4 x 4: the inner ring is a 2 x 2 square"),
])
def test_examples(r, c, expected, why):
    got = ask(grid(r, c))
    assert got == [expected], f"Grid {r} x {c} numbered row by row: expected {expected}, got {got} ({why})."


def test_random_shapes():
    rng = random.Random(25)
    for _ in range(25):
        r, c = rng.randint(1, 7), rng.randint(1, 7)
        g = [[rng.randint(-9, 99) for _ in range(c)] for _ in range(r)]
        got = ask(g)
        want = walker(g)
        assert got == want, f"Grid {g} ({r} x {c}): expected {want}, got {got}. Count: the output must have r * c values."


def test_large():
    rng = random.Random(26)
    g = [[rng.randint(0, 10**6) for _ in range(301)] for _ in range(499)]
    got = ask(g, timeout=10)
    assert got == walker(g), "A 499 x 301 grid: the spiral order is wrong somewhere (check the inner rings)."
