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
    assert run("3\nmilk 2\nbread 1\ncheese 5\n3\n") == [
        "Day 1: expired bread", "Day 2: expired milk", "Day 3: nothing expired", "Left: cheese"]


def test_several_same_day_in_order():
    out = run("3\nz 1\na 1\nm 2\n1\n")
    assert out == ["Day 1: expired z, a", "Left: m"], (
        "Several items can expire on the same day. Deleting them inside 'for item in fridge' "
        "crashes; collect them first. Keep their original order.")


def test_everything_expires():
    assert run("2\nx 1\ny 1\n2\n") == ["Day 1: expired x, y", "Day 2: nothing expired", "Left: nothing"]


def test_zero_days_simulated():
    assert run("1\negg 3\n0\n") == ["Left: egg"], "With D = 0, no day is printed."


def test_empty_fridge():
    assert run("0\n2\n") == ["Day 1: nothing expired", "Day 2: nothing expired", "Left: nothing"]
