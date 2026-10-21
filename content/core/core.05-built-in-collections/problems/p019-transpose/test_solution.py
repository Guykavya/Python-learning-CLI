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
    assert run("2 3\n1 2 3\n4 5 6\n") == ["1 4", "2 5", "3 6"]


def test_single_row():
    assert run("1 3\n7 8 9\n") == ["7", "8", "9"], "One row becomes one column."


def test_single_column():
    assert run("3 1\n1\n2\n3\n") == ["1 2 3"], "One column becomes one row."


def test_square():
    assert run("2 2\n1 2\n3 4\n") == ["1 3", "2 4"]


def test_one_by_one():
    assert run("1 1\n-5\n") == ["-5"]
