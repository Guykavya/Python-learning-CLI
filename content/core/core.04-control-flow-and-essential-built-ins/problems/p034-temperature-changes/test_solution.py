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
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or an input() call waiting for a line that never comes.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

def test_example():
    assert run("30 32 31 31 35\n") == ["Day 2: +2", "Day 3: -1", "Day 4: 0", "Day 5: +4", "Biggest rise: +4 on day 5"], (
        "Changes start at day 2. Rises have +, no change is 0.")


def test_tie_reports_earliest():
    out = run("10 13 10 13\n")
    assert out[-1] == "Biggest rise: +3 on day 2", "Two rises of 3: report the earliest day. Use > not >=."


def test_no_rises():
    assert run("40 38 38 20\n") == ["Day 2: -2", "Day 3: 0", "Day 4: -18", "No rises"], (
        "No change is ever positive, so print No rises.")


def test_negative_temperatures():
    assert run("-5 -2 -9\n") == ["Day 2: +3", "Day 3: -7", "Biggest rise: +3 on day 2"], (
        "Negative temperatures: -2 minus -5 is +3.")


def test_not_enough():
    assert run("25\n") == ["Not enough data"], "One day has no change."
    assert run("\n") == ["Not enough data"], "No days at all."


def test_two_days():
    assert run("1 1\n") == ["Day 2: 0", "No rises"], "Two equal days: one change of 0."
