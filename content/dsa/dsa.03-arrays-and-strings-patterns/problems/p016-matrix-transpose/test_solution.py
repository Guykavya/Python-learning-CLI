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


def transposed(g):
    return [" ".join(str(g[i][j]) for i in range(len(g))) for j in range(len(g[0]))]


@pytest.mark.parametrize("g, expected, why", [
    ([[1, 2, 3], [4, 5, 6]], ["1 4", "2 5", "3 6"], "the example: 2 x 3 becomes 3 x 2"),
    ([[1, 2], [3, 4]], ["1 3", "2 4"], "a square grid: the diagonal 1, 4 stays"),
    ([[7]], ["7"], "1 x 1"),
    ([[1, 2, 3, 4]], ["1", "2", "3", "4"], "one row becomes one column: print 4 lines"),
    ([[1], [2], [3]], ["1 2 3"], "one column becomes one row: print 1 line"),
    ([[1, 2], [3, 4], [5, 6]], ["1 3 5", "2 4 6"], "3 x 2 becomes 2 x 3: print c = 2 lines of r = 3 values"),
    ([[-1, 0, 10**9]], ["-1", "0", "1000000000"], "negative and big values"),
])
def test_examples(g, expected, why):
    got = ask(g)
    assert got == expected, f"Grid {g}: expected {expected}, got {got} ({why})."


def test_random():
    rng = random.Random(23)
    for _ in range(15):
        r, c = rng.randint(1, 6), rng.randint(1, 6)
        g = [[rng.randint(-9, 9) for _ in range(c)] for _ in range(r)]
        got = ask(g)
        assert got == transposed(g), (
            f"Grid {g} ({r} x {c}): expected {transposed(g)}, got {got}. Output has c lines; line j is column j.")


def test_large():
    rng = random.Random(24)
    g = [[rng.randint(-10**9, 10**9) for _ in range(625)] for _ in range(400)]
    got = ask(g, timeout=10)
    assert got == [" ".join(map(str, col)) for col in zip(*g)], (
        "A 400 x 625 grid was not transposed correctly. Print 625 lines of 400 values.")
