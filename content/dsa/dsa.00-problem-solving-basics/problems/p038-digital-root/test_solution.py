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
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]


import ast

import pytest


@pytest.mark.parametrize("given, root, rounds", [
    ("38", 2, 2), ("99", 9, 2), ("12345", 6, 2), ("5", 5, 0), ("19999999999", 1, 3), ("18", 9, 1),
    ("1" + "9" * 22, 1, 4),
])
def test_examples(given, root, rounds):
    got = run(given + "\n")
    exp = [f"root {root}", f"rounds {rounds}"]
    assert got == exp, f"For n = {given} expected {exp}, got {got}"


def test_zero():
    got = run("0\n")
    assert got == ["root 0", "rounds 0"], (
        f"0 already has one digit: root 0, rounds 0. Got {got}")


def test_nine():
    got = run("9\n")
    assert got == ["root 9", "rounds 0"], (
        f"9 already has one digit, so no rounds happen. Got {got}")


def test_ten():
    got = run("10\n")
    assert got == ["root 1", "rounds 1"], (
        f"10 has two digits: one round gives 1. Got {got}. "
        "If you got 'root 10', your loop condition should be n >= 10, not n > 10.")


def test_hundred_nines():
    got = run("9" * 100 + "\n")
    assert got == ["root 9", "rounds 2"], (
        f"100 nines -> 900 -> 9, so two rounds. Got {got}. Check that total is reset every round.")


def test_hundred_digits():
    n = "1" + "0" * 99
    got = run(n + "\n")
    assert got == ["root 1", "rounds 1"], f"10^99 has digit sum 1, one round. Got {got}"


def test_no_string_conversion():
    tree = ast.parse(SOLUTION.read_text())
    calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert not calls & {"str", "list", "map", "sorted", "repr", "format"}, (
        "Solve it with % and // only. Do not turn the number into a string.")
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            assert not (isinstance(node.iter, ast.Name)), (
                "Looping 'for ch in ...' over the input text is string work. Use % 10 and // 10 on the number.")
