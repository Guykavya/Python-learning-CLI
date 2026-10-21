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

import ast


def tree():
    return ast.parse(SOLUTION.read_text())


def calls(name):
    """How many times a function with this name is called in your code."""
    return sum(1 for n in ast.walk(tree())
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name)


def has(node_type):
    return any(isinstance(n, node_type) for n in ast.walk(tree()))

def test_example():
    assert run("3 2\nmove 1\nright\nmove 5\nwhere\nstop\n") == [
        "Bumped into wall at (2, 1)", "At (2, 1) facing east", "Final: (2, 1) facing east", "Steps: 3"], (
        "Up 1 to (0, 1), turn right to face east, then 2 steps reach x = 2 and the third bumps.")


def test_stop_at_once():
    assert run("5 5\nstop\n") == ["Final: (0, 0) facing north", "Steps: 0"], "Start at (0, 0) facing north."


def test_turns():
    out = run("4 4\nleft\nwhere\nturn around\nwhere\nright\nwhere\nright\nright\nright\nright\nwhere\nstop\n")
    assert out[:4] == ["At (0, 0) facing west", "At (0, 0) facing east", "At (0, 0) facing south",
                       "At (0, 0) facing south"], (
        f"Got {out[:4]}. left from north is west; turn around from west is east; right from east is south; "
        "four rights bring you back.")


def test_wall_immediately():
    assert run("3 3\nleft\nmove 2\nturn around\nturn around\nleft\nmove 1\nstop\n") == [
        "Bumped into wall at (0, 0)", "Bumped into wall at (0, 0)", "Final: (0, 0) facing south", "Steps: 0"], (
        "Facing west or south from (0, 0), the first step already hits a wall. Do not move or count it.")


def test_full_walk():
    stdin = "4 3\nmove 2\nright\nmove 3\nright\nmove 1\nwhere\nleft\nmove 1\nstop\n"
    assert run(stdin) == ["At (3, 1) facing south", "Bumped into wall at (3, 1)", "Final: (3, 1) facing east",
                          "Steps: 6"], "Trace on paper: north 2, east 3, south 1, then east bumps at x = 3."


def test_unknown_and_blank():
    out = run("2 2\n\nfly\nmove\nmove -1\nmove x\nturn\nstop\n")
    assert out == ["Unknown: fly", "Unknown: move", "Unknown: move -1", "Unknown: move x", "Unknown: turn",
                   "Final: (0, 0) facing north", "Steps: 0"], (
        "Blank lines are ignored. move needs a whole number of 1 or more; 'turn' alone is not 'turn around'.")


def test_uses_match():
    assert has(ast.Match), "Use match/case for the commands."
