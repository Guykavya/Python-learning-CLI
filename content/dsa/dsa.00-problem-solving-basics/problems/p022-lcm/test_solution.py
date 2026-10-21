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


def ref_lcm(a: int, b: int) -> int:
    x, y = a, b
    while y:
        x, y = y, x % y
    return a // x * b


@pytest.mark.parametrize("a, b", [
    (4, 6), (21, 6), (6, 21), (8, 9), (12, 18), (14, 35), (100, 75),
])
def test_small(a, b):
    expected = ref_lcm(a, b)
    got = run(f"{a}\n{b}\n")
    assert got == [str(expected)], f"For a={a}, b={b} expected {expected}, got {got}."


def test_equal():
    got = run("7\n7\n")
    assert got == ["7"], f"lcm(7, 7) is 7, got {got}."


def test_one():
    assert run("1\n9\n") == ["9"], "lcm(1, 9) is 9: 1 divides every number."
    assert run("1\n1\n") == ["1"], "lcm(1, 1) is 1."


def test_one_divides_other():
    assert run("5\n20\n") == ["20"], "5 divides 20, so lcm(5, 20) is 20."
    assert run("20\n5\n") == ["20"], "The order of the inputs must not matter: lcm(20, 5) is 20."


def test_exact_integer_output():
    got = run("4\n6\n")
    assert got == ["12"], (
        f"Expected 12, got {got}. If you see 12.0, you used / instead of //.")


def test_big_with_common_factor():
    a = 2 ** 40 * 3 ** 10
    b = 2 ** 35 * 5 ** 12
    expected = ref_lcm(a, b)
    got = run(f"{a}\n{b}\n", timeout=3)
    assert got == [str(expected)], (
        f"Expected {expected}, got {got}. Use // so the big result stays exact.")


def test_big_coprime_fast():
    a = 10 ** 18
    b = 10 ** 18 - 1
    got = run(f"{a}\n{b}\n", timeout=3)
    assert got == [str(a * b)], (
        f"These two numbers share no factor, so the LCM is their product {a * b}. Got {got}. "
        "Use Euclid's algorithm for the GCD; counting up through multiples is far too slow here.")


def test_big_coprime_primes():
    a = 999999999989
    b = 1000000007
    got = run(f"{a}\n{b}\n", timeout=3)
    assert got == [str(a * b)], f"Both are prime, so the LCM is {a * b}. Got {got}."


def test_no_imports():
    tree = ast.parse(SOLUTION.read_text())
    assert not any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree)), (
        "Do not import anything (no math.gcd or math.lcm). Write Euclid's algorithm with a while loop.")
    assert not called_names() & {"gcd", "lcm"}, "Write the GCD yourself with a loop."
