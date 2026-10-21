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


def test_blinker_one_step():
    assert run("5 5 1\n.....\n..#..\n..#..\n..#..\n.....\n") == [".....", ".....", ".###.", ".....", "....."], (
        "All cells change at once. If you update in place, cells read already-changed neighbours.")


def test_blinker_two_steps():
    assert run("5 5 2\n.....\n..#..\n..#..\n..#..\n.....\n") == [".....", "..#..", "..#..", "..#..", "....."]


def test_zero_generations():
    assert run("2 3 0\n#.#\n...\n") == ["#.#", "..."]


def test_block_is_stable():
    assert run("4 4 3\n....\n.##.\n.##.\n....\n") == ["....", ".##.", ".##.", "...."]


def test_edges_are_dead():
    assert run("3 3 1\n###\n...\n...\n") == [".#.", ".#.", "..."], (
        "Cells outside the grid are dead; do not wrap around.")


def test_glider():
    start = "6 6 4\n.#....\n..#...\n###...\n......\n......\n......\n"
    assert run(start) == ["......", "..#...", "...#..", ".###..", "......", "......"], (
        "After 4 generations a glider has moved one step down and right.")
