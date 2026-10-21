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
    assert run("3\n1 2\n3 4 5\n\n") == ["1 2 3 4 5", "Total: 15", "Longest row: 1"]


def test_zero_rows():
    assert run("0\n") == ["(empty)", "Total: 0", "Longest row: none"]


def test_all_rows_empty():
    assert run("2\n\n\n") == ["(empty)", "Total: 0", "Longest row: 0"], (
        "Two empty rows tie for longest (length 0); use the first, index 0.")


def test_tie_takes_first():
    out = run("3\n1\n2 3\n4 5\n")
    assert out[2] == "Longest row: 1", "Rows 1 and 2 both have 2 numbers; use the first."


def test_order_kept():
    assert run("2\n9 8\n7\n")[0] == "9 8 7", "Flatten row by row, left to right."
