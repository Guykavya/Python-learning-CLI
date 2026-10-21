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
    assert run("3 8 1 6\n") == ["(3, 8, 1, 6)", "(1, 8)", "(8, 6)"]


def test_single_number():
    assert run("5\n") == ["(5,)", "(5, 5)", "()"], (
        "A one-item tuple prints as (5,) and an empty tuple as (). Print real tuples, "
        "do not build the text by hand.")


def test_one_even():
    out = run("1 4 7\n")
    assert out[2] == "(4,)", "One even number gives a one-item tuple: (4,)."


def test_negatives():
    assert run("-2 -9\n") == ["(-2, -9)", "(-9, -2)", "(-2,)"]
