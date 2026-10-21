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

import pytest


def test_example():
    assert run("the quick brown fox jumps\n") == ["Longest: quick (5 letters)", "Shortest: the (3 letters)"], (
        "quick, brown and jumps tie at 5: report the first. the and fox tie at 3: report the first.")


@pytest.mark.parametrize("line, longest, shortest", [
    ("a bb ccc", "ccc", "a"),
    ("zebra ant", "zebra", "ant"),
    ("same size here", "same", "same"),
    ("one", "one", "one"),
])
def test_cases(line, longest, shortest):
    out = run(line + "\n")
    assert out[0].startswith(f"Longest: {longest} "), f"For {line!r} the longest (first on ties) is {longest!r}; got {out}"
    assert out[1].startswith(f"Shortest: {shortest} "), f"For {line!r} the shortest (first on ties) is {shortest!r}; got {out}"


def test_singular():
    assert run("I am\n")[1] == "Shortest: I (1 letter)", "One letter: use the singular 'letter'."


def test_no_words():
    assert run("   \n") == ["No words"], "No words: max() of nothing would crash. Check first or use default=."


def test_uses_key():
    used = [n for n in ast.walk(tree()) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id in ("min", "max") and any(k.arg == "key" for k in n.keywords)]
    assert used, "Call max(...) or min(...) with key=len."
