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
    assert run("4 -3 7 -8 0 5\n") == ["[16, 64, 0]", "[4, 0, 7, 0, 0, 5]", "[0, 1, 2]"], (
        "0 is even, so its square 0 is included. -8 % 3 is 1 in Python.")


def test_empty():
    assert run("\n") == ["[]", "[]", "[]"], "An empty line gives three empty lists."


def test_no_evens():
    out = run("1 3 5\n")
    assert out[0] == "[]", "No even numbers means an empty first list."
    assert out[2] == "[0, 1, 2]", "1 % 3, 3 % 3 and 5 % 3 are 1, 0 and 2."


def test_all_negative():
    assert run("-1 -2\n")[1] == "[0, 0]", "Every negative becomes 0, but the list keeps its length."
