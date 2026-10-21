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
    assert run("cat\nThe Cat sat. The cat ran!\n") == ["Found 'cat' as word 2"], (
        "Ignore capitals: 'Cat' matches 'cat'. Report only the first match, counting words from 1.")


@pytest.mark.parametrize("target, sentence, expected", [
    ("ran", "The Cat sat. The cat ran!", "Found 'ran' as word 6"),
    ("SAT", "The Cat sat. The cat ran!", "Found 'SAT' as word 3"),
    ("the", "The end", "Found 'the' as word 1"),
    ("why", "Why? Because!", "Found 'why' as word 1"),
])
def test_found(target, sentence, expected):
    got = run(f"{target}\n{sentence}\n")
    assert got == [expected], (
        f"Target {target!r} in {sentence!r}: expected [{expected!r}], got {got}. "
        "Strip .,!? from each word and compare in lower case.")


@pytest.mark.parametrize("target, sentence", [("dog", "The Cat sat."), ("cat", "concatenate cats"), ("x", "")])
def test_not_found(target, sentence):
    got = run(f"{target}\n{sentence}\n")
    assert got == [f"'{target}' not found"], (
        f"{target!r} is not a word of {sentence!r}. Expected exactly one 'not found' line, got {got}. "
        "Is your else lined up with the for, not the if?")


def test_uses_for_else():
    loops = [n for n in ast.walk(tree()) if isinstance(n, ast.For)]
    assert any(loop.orelse for loop in loops), (
        "Use a for loop with an else clause for the 'not found' case.")
