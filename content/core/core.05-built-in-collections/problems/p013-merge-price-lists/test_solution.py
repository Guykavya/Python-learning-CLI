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
    assert run("pen=10 ink=40 pad=25\nink=45 pad=25 tape=15\n") == [
        "ink: 45", "pad: 25", "pen: 10", "tape: 15", "Changed: ink"], (
        "The new list wins (ink is 45). pad is in both with the same price, so it did not change.")


def test_old_empty():
    assert run("\na=1 b=2\n") == ["a: 1", "b: 2", "Changed: none"], "An empty line is an empty dict."


def test_new_empty():
    assert run("z=5 y=6\n\n") == ["y: 6", "z: 5", "Changed: none"], "Output is sorted by item name."


def test_several_changes_sorted():
    out = run("c=1 b=1 a=1\nc=2 a=3 b=1\n")
    assert out[-1] == "Changed: a, c", "List changed items sorted and joined with ', '."


def test_new_wins():
    out = run("tea=10\ntea=12\n")
    assert out[0] == "tea: 12", "When an item is in both, the NEW price wins: old | new."


def test_numeric_compare():
    out = run("x=07\nx=7\n")
    assert out == ["x: 7", "Changed: none"], "Compare prices as numbers: 07 and 7 are the same price."
