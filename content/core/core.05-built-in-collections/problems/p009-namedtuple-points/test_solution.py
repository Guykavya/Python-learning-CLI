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
    assert run("3\n1 1\n3 4\n-4 3\n") == [
        "Points: 3", "Farthest: Point(x=3, y=4)", "Moved: Point(x=4, y=4)", "Sum of x: 0"], (
        "(3, 4) and (-4, 3) are equally far (25). Keep the first one.")


def test_single_point():
    assert run("1\n0 0\n") == [
        "Points: 1", "Farthest: Point(x=0, y=0)", "Moved: Point(x=1, y=0)", "Sum of x: 0"]


def test_negative_far():
    out = run("2\n1 2\n-10 0\n")
    assert out[1] == "Farthest: Point(x=-10, y=0)", "Distance uses x*x + y*y, so negatives count."
    assert out[2] == "Moved: Point(x=-9, y=0)", "Moved adds 1 to x using _replace."


def test_uses_namedtuple_display():
    out = run("1\n2 5\n")
    assert out[1] == "Farthest: Point(x=2, y=5)", (
        "Create the type with namedtuple('Point', ['x', 'y']) so it prints as Point(x=2, y=5).")
