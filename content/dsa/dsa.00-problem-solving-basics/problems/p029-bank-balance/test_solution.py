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


def bank(opening: int, *ops) -> list[str]:
    text = f"{opening}\n{len(ops)}\n" + "".join(f"{op}\n{amount}\n" for op, amount in ops)
    return run(text)


def test_example_one():
    got = bank(100, ("W", 30), ("W", 100), ("D", 50), ("W", 120))
    assert got == ["balance 70", "declined", "balance 120", "balance 0", "final 0"], (
        f"Expected balance 70, declined, balance 120, balance 0, final 0. Got {got}.")


def test_example_two():
    got = bank(10, ("D", -5), ("X", 5), ("W", 0))
    assert got == ["invalid amount", "unknown operation", "invalid amount", "final 10"], (
        f"Expected invalid amount, unknown operation, invalid amount, final 10. Got {got}.")


def test_no_operations():
    got = bank(5)
    assert got == ["final 5"], f"With 0 operations print only 'final 5'. Got {got}."


def test_withdraw_exact_balance():
    got = bank(50, ("W", 50))
    assert got == ["balance 0", "final 0"], (
        f"Withdrawing exactly the whole balance is allowed. Got {got}. Use amount > balance for declined.")


def test_declined_keeps_balance():
    got = bank(20, ("W", 21), ("D", 1), ("W", 21))
    assert got == ["declined", "balance 21", "balance 0", "final 0"], (
        f"A declined withdrawal must not change the balance. Got {got}.")


def test_zero_opening_withdraw():
    got = bank(0, ("W", 1), ("D", 1), ("W", 1))
    assert got == ["declined", "balance 1", "balance 0", "final 0"], (
        f"Starting from 0: W 1 is declined, D 1 gives 1, W 1 gives 0. Got {got}.")


def test_negative_withdraw_is_invalid():
    got = bank(10, ("W", -5))
    assert got == ["invalid amount", "final 10"], (
        f"W -5 is an invalid amount, got {got}. Check the amount before checking the balance; "
        "otherwise subtracting -5 would raise the balance to 15.")


def test_unknown_before_amount_check():
    got = bank(10, ("Q", -5), ("Z", 0))
    assert got == ["unknown operation", "unknown operation", "final 10"], (
        f"An unknown letter is reported as 'unknown operation' even when the amount is also bad. Got {got}.")


def test_unknown_keeps_reading_in_step():
    got = bank(10, ("X", 5), ("D", 7))
    assert got == ["unknown operation", "balance 17", "final 17"], (
        f"Even for an unknown letter you must read its amount line, or every later read shifts. Got {got}.")


def test_lowercase_is_unknown():
    got = bank(10, ("d", 5), ("w", 5))
    assert got == ["unknown operation", "unknown operation", "final 10"], (
        f"Letters are case-sensitive: 'd' and 'w' are unknown operations. Got {got}.")


def test_long_word_is_unknown():
    got = bank(10, ("DD", 5), ("Deposit", 5))
    assert got == ["unknown operation", "unknown operation", "final 10"], (
        f"Only a line that is exactly 'D' or 'W' is valid. Compare the whole line with ==. Got {got}.")


def test_big_amounts():
    got = bank(1000000000, ("D", 1000000000), ("W", 2000000000), ("W", 1))
    assert got == ["balance 2000000000", "balance 0", "declined", "final 0"], (
        f"Expected balance 2000000000, balance 0, declined, final 0. Got {got}.")


def test_many_operations():
    ops = [("D", 3), ("W", 2)] * 5000
    got = bank(0, *ops)
    assert len(got) == 10001, f"Expected 10000 operation lines plus the final line, got {len(got)} lines."
    assert got[-1] == "final 5000", f"Each D 3 / W 2 pair adds 1, so the final balance is 5000. Got {got[-1]!r}."


def test_no_string_methods():
    tree = ast.parse(SOLUTION.read_text())
    methods = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert not methods, (
        f"Do not use methods such as {', '.join(sorted(methods))}. Compare the whole line with ==, "
        "for example op == \"D\".")
