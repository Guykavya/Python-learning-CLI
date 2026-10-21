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
    assert run("100 4 200 1 3 2 101 4\n") == ["Length: 4", "Run: 1 to 4"]


def test_empty():
    assert run("\n") == ["Length: 0"]


def test_single():
    assert run("7\n") == ["Length: 1", "Run: 7 to 7"]


def test_tie_smallest_start():
    assert run("10 11 1 2 5\n") == ["Length: 2", "Run: 1 to 2"], (
        "Two runs of length 2: report the one with the smaller first value.")


def test_negatives_and_repeats():
    assert run("-1 0 0 -2 1 1\n") == ["Length: 4", "Run: -2 to 1"], "Repeats do not lengthen a run."


def test_large_one_run_fast():
    n = 200000
    nums = list(range(n, 0, -1))
    out = run(" ".join(map(str, nums)) + "\n")
    assert out == [f"Length: {n}", f"Run: 1 to {n}"], (
        "One long run of 200,000 values. Walking from every value, or using `in` on a list, "
        "is O(n^2). Start walks only where x - 1 is missing, and use a set.")
