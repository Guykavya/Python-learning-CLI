import ast
import subprocess
import sys
from pathlib import Path

import pytest

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


def called_names() -> set[str]:
    """Names of every plain function call in your solution, e.g. {'print', 'int', 'input'}."""
    tree = ast.parse(SOLUTION.read_text())
    return {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


@pytest.mark.parametrize("s, expected", [
    ("1101", "13"), ("1", "1"), ("10", "2"), ("11111111", "255"), ("10000000000", "1024"), ("101010", "42"),
])
def test_valid(s, expected):
    got = run(s + "\n")
    assert got == [expected], (
        f"For {s!r} expected {expected}, got {got}. For each digit: value = value * 2 + digit.")


def test_zero():
    assert run("0\n") == ["0"], "The binary number 0 is 0."
    assert run("0000\n") == ["0"], "0000 is still 0."


def test_leading_zeros():
    got = run("0001\n")
    assert got == ["1"], f"0001 is 1: leading zeros add nothing. Got {got}."


def test_64_ones():
    got = run("1" * 64 + "\n")
    assert got == [str(2 ** 64 - 1)], f"64 ones is 2^64 - 1 = {2 ** 64 - 1}. Got {got}."


def test_64_chars_with_leading_one():
    s = "1" + "0" * 63
    got = run(s + "\n")
    assert got == [str(2 ** 63)], f"1 followed by 63 zeros is 2^63 = {2 ** 63}. Got {got}."


@pytest.mark.parametrize("s", ["102", "2", "abc", "10 1", "-101", "1.0", "1b", "b1", "0x1", "11112"])
def test_invalid(s):
    got = run(s + "\n")
    assert got == ["invalid"], (
        f"{s!r} contains a character that is not 0 or 1, so print exactly one line 'invalid'. Got {got}.")


def test_no_int_base_or_methods():
    tree = ast.parse(SOLUTION.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "int":
            assert len(node.args) < 2 and not node.keywords, (
                "Do not use int(s, 2). Build the value yourself: value = value * 2 + digit.")
    methods = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert not methods, (
        f"Do not use string methods such as {', '.join(sorted(methods))}. "
        "Check each character with == \"0\" and == \"1\".")
    assert not called_names() & {"eval", "exec"}, "Do not use eval() or exec()."
