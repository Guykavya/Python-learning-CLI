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

def test_example():
    assert run("milk, bread ,eggs\n") == ["1. milk", "2. bread", "3. eggs", "Total: 3 items"], (
        "Number from 1 and strip the spaces around each item.")


def test_one_item():
    assert run("  tea \n") == ["1. tea", "Total: 1 item"], "A single item uses the word 'item'."


def test_blank():
    assert run("   \n") == ["(no items)"], "A blank line has no items. Check it before splitting."


def test_many():
    items = [f"thing{n}" for n in range(12)]
    want = [f"{i}. {t}" for i, t in enumerate(items, start=1)] + ["Total: 12 items"]
    assert run(",".join(items) + "\n") == want, "Numbers continue to 10, 11, 12 without gaps."


def test_uses_enumerate_not_range():
    assert calls("enumerate") >= 1, "Use enumerate(items, start=1)."
    assert calls("range") == 0, "Do not use range in this problem. enumerate gives the numbers."
