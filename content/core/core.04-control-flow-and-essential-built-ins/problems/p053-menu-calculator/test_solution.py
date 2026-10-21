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

MENU = ["Menu:", "1) add", "2) subtract", "3) multiply", "4) divide", "5) power", "?) show this menu", "q) quit"]


def after_menu(stdin):
    out = run(stdin)
    assert out[:8] == MENU, f"The program must start by printing the menu exactly. First lines were: {out[:8]}"
    return out[8:]


def test_example():
    assert after_menu("1\n2\n3.5\n4\n1\n0\nx\nq\n") == [
        "Result: 5.50", "Cannot divide by zero", "Unknown choice: x", "Done. 1 calculation."], (
        "Compare with the example. Division by zero is refused and not counted.")


@pytest.mark.parametrize("choice, a, b, want", [
    ("1", "2", "3", "Result: 5.00"),
    ("2", "2", "3", "Result: -1.00"),
    ("3", "2.5", "4", "Result: 10.00"),
    ("4", "7", "2", "Result: 3.50"),
    ("4", "1", "3", "Result: 0.33"),
    ("5", "2", "10", "Result: 1024.00"),
    ("5", "9", "0.5", "Result: 3.00"),
    ("4", "0", "5", "Result: 0.00"),
])
def test_operations(choice, a, b, want):
    got = after_menu(f"{choice}\n{a}\n{b}\nq\n")
    assert got == [want, "Done. 1 calculation."], (
        f"Choice {choice} with {a} and {b}: expected {want}, got {got}. Read a first, then b; show 2 decimals.")


def test_quit_immediately_plural_zero():
    assert after_menu("q\n") == ["Done. 0 calculations."], "Zero calculations uses the plural."


def test_quit_word_and_capitals():
    assert after_menu("QUIT\n") == ["Done. 0 calculations."], "Choices ignore capitals: QUIT quits."
    assert after_menu("  Q  \n") == ["Done. 0 calculations."], "Strip spaces from the choice."


def test_help_reprints_menu():
    assert after_menu("?\nq\n") == MENU + ["Done. 0 calculations."], "? prints the menu again."


def test_blank_lines_ignored_and_count():
    got = after_menu("\n1\n1\n1\n\n3\n2\n2\n   \nq\n")
    assert got == ["Result: 2.00", "Result: 4.00", "Done. 2 calculations."], (
        "Blank choice lines are ignored without a message. Two results means 'Done. 2 calculations.'")


def test_unknown_choices():
    assert after_menu("6\n0\nadd\nq\n") == [
        "Unknown choice: 6", "Unknown choice: 0", "Unknown choice: add", "Done. 0 calculations."], (
        "Only 1 to 5, ?, q and quit are known. Unknown choices must not read any numbers.")


def test_divide_by_zero_point_zero():
    assert after_menu("4\n5\n0.0\nq\n") == ["Cannot divide by zero", "Done. 0 calculations."], (
        "0.0 is zero too. Check b == 0 before dividing.")


def test_uses_match():
    assert has(ast.Match), "Use match/case for the menu choice."
