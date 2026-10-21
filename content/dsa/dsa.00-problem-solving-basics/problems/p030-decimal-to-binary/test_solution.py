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


@pytest.mark.parametrize("n, expected", [
    (13, "1101"), (6, "110"), (1, "1"), (2, "10"), (5, "101"), (255, "11111111"), (1024, "10000000000"),
])
def test_examples(n, expected):
    got = run(f"{n}\n")
    assert got == [expected], (
        f"For {n} expected {expected}, got {got}. If your digits are reversed, put each new bit in front.")


def test_zero():
    got = run("0\n")
    assert got == ["0"], f"0 in binary is 0. Got {got}. With while n > 0 the loop never runs, so handle 0 separately."


def test_reversal():
    got = run("6\n")
    assert got == ["110"], (
        f"6 is 110 in binary, got {got}. If you got 011, you added each bit to the end; add it to the front.")


@pytest.mark.parametrize("n", [7, 100, 123456789, 2 ** 59, 2 ** 60 - 1, 10 ** 18, 999999999999999999])
def test_various(n):
    expected = format(n, "b")
    got = run(f"{n}\n")
    assert got == [expected], f"For {n} expected {expected}, got {got}."


def test_no_builtin_conversion():
    tree = ast.parse(SOLUTION.read_text())
    assert not called_names() & {"bin", "format", "hex", "oct"}, (
        "Do not use bin(), format(), hex() or oct(). Build the digits with % 2 and // 2.")
    methods = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert not methods, f"Do not use methods such as {', '.join(sorted(methods))}. Use % 2 and // 2."
    for node in ast.walk(tree):
        if isinstance(node, ast.FormattedValue) and node.format_spec is not None:
            spec = ast.unparse(node.format_spec)
            assert not any(ch in spec for ch in "bxXo"), (
                "Do not use a format spec like f\"{n:b}\". Build the binary digits yourself.")
    assert not any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(tree)), (
        "Do not import anything.")
