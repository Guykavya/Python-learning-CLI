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


def test_simple():
    assert run("hello\n") == ["HELLO!"], "Change to capitals with .upper() and add one '!'."


def test_empty_line():
    assert run("\n") == ["(blank)"], "An empty line should print (blank). An empty string is falsy."


def test_only_spaces():
    assert run("     \n") == ["(blank)"], (
        "A line of spaces is truthy as it is. Strip it first, then test it.")


def test_strips_and_keeps_one_bang():
    assert run("   wow!  \n") == ["WOW!"], (
        "Strip the spaces first, then check endswith('!') so you do not print WOW!!.")


@pytest.mark.parametrize("given, expected", [("0", "0!"), ("False", "FALSE!"), ("hi there", "HI THERE!"), ("!", "!")])
def test_truthy_strings(given, expected):
    got = run(given + "\n")
    assert got == [expected], (
        f"Input {given!r} should give {expected!r}, got {got}. Any non-empty string is truthy, even '0'.")
