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
    assert run("2\n123\n45\n3\n0 0 9\n1 1 5\n1 0 7\n") == [
        "Original:", "123", "45", "Edited:", "923", "75", "Changed cells: 2"]


def test_original_unchanged():
    out = run("1\n000\n1\n0 1 8\n")
    assert out[1] == "000", (
        "The original must not change. work = grid is an alias, and grid.copy() is shallow: "
        "both share the rows. Copy each row.")
    assert out[3] == "080" and out[4] == "Changed cells: 1"


def test_no_edits():
    assert run("1\n42\n0\n") == ["Original:", "42", "Edited:", "42", "Changed cells: 0"]


def test_edit_back_to_original():
    out = run("1\n12\n2\n0 0 5\n0 0 1\n")
    assert out[-1] == "Changed cells: 0", "Count differences at the end, not the number of edits."
