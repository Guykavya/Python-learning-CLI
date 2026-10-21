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

import pytest


def test_example():
    assert run("zoya Aarav meera Bhavesh\n") == ["First: Aarav", "Last: zoya", "Longest: Bhavesh"], (
        "Compare ignoring case: zoya is last even though it starts with a small letter.")


def test_capitals_do_not_win():
    assert run("Zara anil\n") == ["First: anil", "Last: Zara", "Longest: Zara"], (
        "Without key=str.lower, 'Zara' < 'anil' because capitals come first. Ignore case.")


def test_equal_ignoring_case_first_wins():
    assert run("amit Amit AMIT\n") == ["First: amit", "Last: amit", "Longest: amit"], (
        "All three are equal ignoring case and length. min and max return the first of equal items.")


@pytest.mark.parametrize("line", ["Kiran", "b A c", "delta Alpha charlie Bravo", "xy XYZ xyz"])
def test_more(line):
    names = line.split()
    want = [f"First: {min(names, key=str.lower)}", f"Last: {max(names, key=str.lower)}",
            f"Longest: {max(names, key=len)}"]
    assert run(line + "\n") == want, f"For {line!r} expected {want}. Print names as typed."


def test_no_names():
    assert run("\n") == ["No names"], "No names: print No names instead of crashing in min()."
