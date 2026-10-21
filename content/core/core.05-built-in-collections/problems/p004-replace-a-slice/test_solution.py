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
    assert run("10 20 30 40 50\n1 3\n7 8 9\n") == ["10 7 8 9 40 50"], (
        "nums[1:3] = [7, 8, 9] replaces 20 and 30 with three numbers, so the list grows.")


def test_shrink():
    assert run("1 2 3 4 5\n0 4\n9\n") == ["9 5"], "Four items replaced by one: the list shrinks."


def test_insert_when_i_equals_j():
    assert run("1 2 3\n1 1\n100 200\n") == ["1 100 200 2 3"], (
        "When i == j the slice is empty. Nothing is removed and the new numbers are inserted.")


def test_delete_with_empty_line():
    assert run("1 2 3 4\n1 3\n\n") == ["1 4"], "An empty replacement deletes the slice."


def test_everything_deleted():
    assert run("5 6\n0 2\n\n") == ["(empty)"], "If nothing is left, print (empty)."


def test_past_the_end():
    assert run("1 2 3\n2 99\n7\n") == ["1 2 7"], (
        "A slice end past the list is cut short, it never raises an error.")


def test_negative_positions():
    assert run("1 2 3 4\n-2 4\n0\n") == ["1 2 0"], "Negative positions count from the end, as usual."
