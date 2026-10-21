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


def to_base(n, b):
    """Independent check used only by the tests."""
    if n == 0:
        return "0"
    s = ""
    m = abs(n)
    while m:
        s = "0123456789ABCDEF"[m % b] + s
        m //= b
    return ("-" if n < 0 else "") + s


@pytest.mark.parametrize("n, b, expected", [
    (255, 16, "FF"), (255, 2, "11111111"), (13, 2, "1101"), (10, 16, "A"), (15, 16, "F"),
    (16, 16, "10"), (100, 7, "202"), (35, 12, "2B"), (1, 2, "1"), (2, 2, "10"),
])
def test_positive(n, b, expected):
    got = run(f"{n}\n{b}\n")
    assert got == [expected], (
        f"n = {n}, b = {b}: expected {expected!r}, got {got}. If the digits are reversed, remember "
        "that % b gives the LAST digit first. Letters must be uppercase.")


def test_negative():
    got = run("-10\n3\n")
    assert got == ["-101"], (
        f"n = -10, b = 3: expected '-101', got {got}. Remember the sign, then convert abs(n).")


def test_negative_hex():
    got = run("-255\n16\n")
    assert got == ["-FF"], f"n = -255, b = 16: expected '-FF', got {got}."


def test_zero():
    got = run("0\n7\n")
    assert got == ["0"], f"n = 0: expected '0', got {got}. The loop does not run for 0, so handle it separately."


def test_base_ten_is_identity():
    for n in [7, 1234567890, -999]:
        got = run(f"{n}\n10\n")
        assert got == [str(n)], f"n = {n}, b = 10: expected {str(n)!r}, got {got}."


@pytest.mark.parametrize("b", [1, 0, -2, 17, 100])
def test_invalid_base(b):
    got = run(f"42\n{b}\n")
    assert got == ["invalid base"], (
        f"b = {b}: expected 'invalid base', got {got}. Only 2..16 are allowed. "
        "(b = 1 would loop forever: 42 // 1 is still 42.)")


def test_invalid_base_with_zero():
    got = run("0\n1\n")
    assert got == ["invalid base"], f"n = 0, b = 1: expected 'invalid base', got {got}. Check the base first."


@pytest.mark.parametrize("n, b", [(10 ** 18, 16), (10 ** 18, 2), (-(10 ** 18), 3), (10 ** 18, 13)])
def test_huge(n, b):
    expected = to_base(n, b)
    got = run(f"{n}\n{b}\n", timeout=3)
    assert got == [expected], f"n = {n}, b = {b}: expected {expected!r}, got {got}."


def test_no_builtin_conversion():
    tree = ast.parse(SOLUTION.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"bin", "hex", "oct", "format"}, (
                f"Do not use {node.func.id}(). Compute the digits with % and //.")
            assert not (node.func.id == "int" and len(node.args) > 1), (
                "Do not use int(x, base). Compute the digits with % and //.")
        if isinstance(node, ast.FormattedValue) and node.format_spec is not None:
            spec = ast.unparse(node.format_spec)
            assert not any(c in spec for c in "bxXo"), (
                "Do not use f-string format codes like :b or :x. Compute the digits with % and //.")
