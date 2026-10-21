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
    assert run("1 5 7 -1 5 3 3 9\n6\n") == ["-1 + 7", "1 + 5", "3 + 3", "Pairs: 3"]


def test_single_half_value():
    assert run("3 1\n6\n") == ["Pairs: 0"], "3 + 3 needs two 3s in the list."


def test_no_reverse_duplicates():
    assert run("2 8 8 2\n10\n") == ["2 + 8", "Pairs: 1"], "Print each pair of values once, with a <= b."


def test_empty():
    assert run("\n5\n") == ["Pairs: 0"]


def test_large_is_fast():
    n = 100000
    nums = list(range(n))
    out = run(" ".join(map(str, nums)) + "\n7\n")
    assert out == ["0 + 7", "1 + 6", "2 + 5", "3 + 4", "Pairs: 4"], (
        "Checking every pair of positions is O(n^2). Use a set or dict of values.")
