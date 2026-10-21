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
    assert run("8 3 5 3 7\n10\n") == ["2 5"], (
        "At position 5 the partner 3 was first seen at position 2.")


def test_no_self_pair():
    assert run("5 1\n10\n") == ["No pair"], "A number cannot pair with itself. Check before storing."


def test_two_equal_numbers():
    assert run("5 5\n10\n") == ["1 2"], "Two different positions holding 5 are a valid pair."


def test_smallest_i():
    assert run("1 1 1 9\n10\n") == ["1 4"], "Keep the FIRST position of each value."


def test_empty():
    assert run("\n0\n") == ["No pair"]


def test_negatives():
    assert run("-3 4 13\n10\n") == ["1 3"]


def test_large_is_fast():
    n = 100000
    nums = list(range(1, n + 1))
    out = run(" ".join(map(str, nums)) + f"\n{2 * n - 1}\n")
    assert out == [f"{n - 1} {n}"], (
        "Checking all pairs is O(n^2), billions of steps here. Use a dict of first positions.")
