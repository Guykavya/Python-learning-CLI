import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program did not finish within {timeout} seconds. Look for an infinite loop, "
            "an input() that waits for more lines than the test gives, or a slow step such as "
            "`in` on a long list inside a loop (use a set or dict instead).") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]


def test_example():
    assert run("3 4\n2\n0 0\n2 3\n") == ["#...", "....", "...#"]


def test_rows_are_independent():
    out = run("3 3\n1\n1 1\n")
    assert out == ["...", ".#.", "..."], (
        "Only the middle cell should change. If every row shows '#', the rows are one shared list: "
        "you probably wrote [['.'] * cols] * rows. Build each row separately.")


def test_no_marks():
    assert run("2 2\n0\n") == ["..", ".."], "With k = 0, print the empty grid."


def test_one_by_one():
    assert run("1 1\n1\n0 0\n") == ["#"]


def test_mark_twice():
    assert run("2 3\n2\n0 2\n0 2\n") == ["..#", "..."], "Marking a cell twice leaves one '#'."


def test_tall_grid():
    out = run("5 1\n1\n4 0\n")
    assert out == [".", ".", ".", ".", "#"], "The first number of a position is the row."
