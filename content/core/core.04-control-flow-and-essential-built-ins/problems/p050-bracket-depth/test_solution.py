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
    assert run("3\n(a + (b * c))\n)(\n((x)\n") == [
        "Balanced, max depth 2", "Unbalanced: unexpected ')' at position 0", "Unbalanced: 1 unclosed '('",
        "Balanced: 1 of 3"], "Check the depth as you go, not just the totals: ')(' has equal counts but is unbalanced."


@pytest.mark.parametrize("line, want", [
    ("", "Balanced, max depth 0"),
    ("no brackets", "Balanced, max depth 0"),
    ("()()()", "Balanced, max depth 1"),
    ("((()))", "Balanced, max depth 3"),
    ("(()())(())", "Balanced, max depth 2"),
    ("())(", "Unbalanced: unexpected ')' at position 2"),
    ("ab)))", "Unbalanced: unexpected ')' at position 2"),
    ("(((", "Unbalanced: 3 unclosed '('"),
    ("(()", "Unbalanced: 1 unclosed '('"),
])
def test_lines(line, want):
    got = run(f"1\n{line}\n")
    assert got[0] == want, (
        f"Line {line!r}: expected {want!r}, got {got[0]!r}. Stop at the first ')' that has nothing to close; "
        "positions count from 0.")


def test_one_message_per_line():
    got = run("1\n)))\n")
    assert got == ["Unbalanced: unexpected ')' at position 0", "Balanced: 0 of 1"], (
        "Only the first problem is reported for a line. Did you forget break?")


def test_lines_are_independent():
    got = run("2\n((\n))\n")
    assert got == ["Unbalanced: 2 unclosed '('", "Unbalanced: unexpected ')' at position 0", "Balanced: 0 of 2"], (
        "Reset the depth for every line. Brackets in one line do not close brackets in another.")


def test_zero_lines():
    assert run("0\n") == ["Balanced: 0 of 0"], "N can be 0."
