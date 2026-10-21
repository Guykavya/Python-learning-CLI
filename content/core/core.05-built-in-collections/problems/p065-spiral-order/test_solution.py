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
    assert run("3 4\n1 2 3 4\n5 6 7 8\n9 10 11 12\n") == ["1 2 3 4 8 12 11 10 9 5 6 7"]


def test_single_row():
    assert run("1 4\n1 2 3 4\n") == ["1 2 3 4"], "A single row must not be walked back again."


def test_single_column():
    assert run("3 1\n1\n2\n3\n") == ["1 2 3"], "A single column must not be walked back up again."


def test_square():
    assert run("3 3\n1 2 3\n4 5 6\n7 8 9\n") == ["1 2 3 6 9 8 7 4 5"]


def test_tall():
    assert run("4 2\n1 2\n3 4\n5 6\n7 8\n") == ["1 2 4 6 8 7 5 3"]


def test_one_cell():
    assert run("1 1\n42\n") == ["42"]
