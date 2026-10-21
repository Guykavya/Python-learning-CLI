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
    assert run("URDLUU\n") == ["Visited: 5", "Revisits: 2", "Final: (0, 2)"]


def test_empty():
    assert run("\n") == ["Visited: 1", "Revisits: 0", "Final: (0, 0)"], (
        "With no moves, the robot has still visited its start cell.")


def test_back_and_forth():
    assert run("RLRL\n") == ["Visited: 2", "Revisits: 3", "Final: (0, 0)"]


def test_straight_line():
    assert run("DDD\n") == ["Visited: 4", "Revisits: 0", "Final: (0, -3)"]


def test_large_is_fast():
    moves = "R" * 100000 + "L" * 100000
    out = run(moves + "\n")
    assert out == ["Visited: 100001", "Revisits: 100000", "Final: (0, 0)"], (
        "Use a set of (x, y) tuples. A list of visited cells makes every check scan the list.")
