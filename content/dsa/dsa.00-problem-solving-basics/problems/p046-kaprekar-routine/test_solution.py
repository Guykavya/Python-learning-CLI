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


def kaprekar(x):
    """Test-side helper (uses strings and sorted, which your solution may not)."""
    if x % 1111 == 0:
        return ["invalid"]
    out = []
    while True:
        digits = sorted(f"{x:04d}")
        small = int("".join(digits))
        big = int("".join(reversed(digits)))
        diff = big - small
        out.append(f"{big:04d} - {small:04d} = {diff:04d}")
        x = diff
        if diff == 6174:
            break
    return out + [f"steps {len(out)}"]


def test_3524():
    got = run("3524\n")
    exp = ["5432 - 2345 = 3087", "8730 - 0378 = 8352", "8532 - 2358 = 6174", "steps 3"]
    assert got == exp, f"For 3524:\nExpected: {exp}\nGot: {got}"


def test_2111_leading_zeros():
    got = run("2111\n")
    exp = ["2111 - 1112 = 0999", "9990 - 0999 = 8991", "9981 - 1899 = 8082",
           "8820 - 0288 = 8532", "8532 - 2358 = 6174", "steps 5"]
    assert got == exp, (
        f"For 2111:\nExpected: {exp}\nGot: {got}\n"
        "The first diff is 999, which must be treated as 0999 (four digits, one zero). "
        "Look at exactly 4 digits, and print with :04d.")


def test_already_6174():
    got = run("6174\n")
    assert got == ["7641 - 1467 = 6174", "steps 1"], (
        f"6174 must still do one step. Expected ['7641 - 1467 = 6174', 'steps 1'], got {got}. "
        "Check for 6174 after the step, not before it.")


def test_1000():
    got = run("1000\n")
    exp = kaprekar(1000)
    assert got == exp, f"For 1000 (three zeros):\nExpected: {exp}\nGot: {got}"


def test_9998():
    got = run("9998\n")
    exp = kaprekar(9998)
    assert got == exp, f"For 9998:\nExpected: {exp}\nGot: {got}"


@pytest.mark.parametrize("x", [1111, 5555, 9999])
def test_invalid(x):
    got = run(f"{x}\n")
    assert got == ["invalid"], f"All digits of {x} are equal: print only 'invalid'. Got {got}"


@pytest.mark.parametrize("x", [1112, 5155, 9831, 1234, 4321, 2005, 7641, 1467, 8082, 6999])
def test_more(x):
    got = run(f"{x}\n")
    exp = kaprekar(x)
    assert got == exp, f"For {x}:\nExpected: {exp}\nGot: {got}"


def test_no_lists_sorting_or_str():
    tree = ast.parse(SOLUTION.read_text())
    calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    banned = calls & {"str", "list", "sorted", "reversed", "map", "tuple", "set"}
    assert not banned, (
        f"Do not use {sorted(banned)}. Build big and small by counting each digit with % 10 and // 10.")
    assert not any(isinstance(n, (ast.List, ast.ListComp)) for n in ast.walk(tree)), (
        "Do not use lists. Count how many times each digit appears instead of sorting.")
    methods = [n.func.attr for n in ast.walk(tree)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
    assert not methods, f"Do not use methods such as {methods}. Use % and // on the number."
