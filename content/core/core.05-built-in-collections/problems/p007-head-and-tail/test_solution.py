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
    assert run("4 8 15 16 23 42\n") == [
        "First: 4", "Last: 42", "Middle: 8 15 16 23", "Middle sum: 62"]


def test_two_numbers():
    assert run("1 2\n") == ["First: 1", "Last: 2", "Middle: (none)", "Middle sum: 0"], (
        "With exactly two numbers the starred name collects nothing: an empty list, whose sum is 0.")


def test_three_numbers():
    assert run("-5 10 -5\n") == ["First: -5", "Last: -5", "Middle: 10", "Middle sum: 10"]


def test_numbers_not_strings():
    out = run("1 2 3 4\n")
    assert out[3] == "Middle sum: 5", "Convert to int before summing."
