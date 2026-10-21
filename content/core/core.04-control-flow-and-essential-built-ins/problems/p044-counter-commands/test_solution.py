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
    stdin = "add 5\ndouble\nsub 3\nshow\nadd\nfly away\nquit\n"
    assert run(stdin) == ["Counter: 7", "Missing number", "Unknown command: fly away", "Final: 7"], (
        "add 5 -> 5, double -> 10, sub 3 -> 7. 'add' alone is Missing number.")


def test_quit_immediately():
    assert run("quit\n") == ["Final: 0"], "The counter starts at 0."


def test_negative_numbers_and_reset():
    assert run("add -4\nshow\nsub -10\nshow\nreset\nshow\nquit\n") == [
        "Counter: -4", "Counter: 6", "Counter: 0", "Final: 0"], "add -4 adds a negative number; sub -10 adds 10."


def test_blank_lines_ignored():
    assert run("\n   \nadd 2\n\nquit\n") == ["Final: 2"], "Blank lines split into [], which should be ignored."


def test_wrong_lengths_are_unknown():
    assert run("add 1 2\ndouble it\nsub\nquit\n") == [
        "Unknown command: add 1 2", "Unknown command: double it", "Missing number", "Final: 0"], (
        "Sequence patterns check the number of words: 'add 1 2' has three words and matches no command pattern.")


def test_stops_at_quit():
    assert run("add 1\nquit\nadd 100\n") == ["Final: 1"], "Nothing after quit is read."


def test_uses_match():
    assert has(ast.Match), "Use match/case on the list of words."
    assert has(ast.MatchSequence), "Use sequence patterns such as case ['add', n]:"
