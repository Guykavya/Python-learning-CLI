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
    assert run("2 3\n1 2 3\n4 5 6\n") == ["1 2 3 = 6", "4 5 6 = 15", "Columns: 5 7 9", "Total: 21"]


def test_tall():
    assert run("3 1\n1\n2\n3\n") == ["1 = 1", "2 = 2", "3 = 3", "Columns: 6", "Total: 6"], (
        "With one column there is one column sum. Loop columns over range(c).")


def test_wide():
    assert run("1 4\n1 -1 2 -2\n") == ["1 -1 2 -2 = 0", "Columns: 1 -1 2 -2", "Total: 0"]
