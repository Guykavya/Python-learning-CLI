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
    assert run("a b c d e\n2\n") == ["d e a b c"]


def test_zero():
    assert run("a b c\n0\n") == ["a b c"]


def test_bigger_than_length():
    assert run("a b c d e\n7\n") == ["d e a b c"], "Rotating 5 items by 7 equals rotating by 2. Use k % n."


def test_negative_rotates_left():
    assert run("a b c d e\n-1\n") == ["b c d e a"], "-1 rotates left by one. -1 % 5 is 4."


def test_empty():
    assert run("\n3\n") == ["(empty)"], "Guard the empty list: k % 0 raises ZeroDivisionError."


def test_full_turn():
    assert run("x y\n4\n") == ["x y"]
