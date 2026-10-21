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


def expected(p):
    checks = [len(p) >= 8, any(c.isdigit() for c in p), any(c.isupper() for c in p), all(c.isalnum() for c in p)]
    labels = ["Length 8+", "Has digit", "Has capital", "Only letters and digits"]
    out = [f"{l}: {'yes' if c else 'no'}" for l, c in zip(labels, checks)]
    return out + ["Strong" if all(checks) else "Weak"]


@pytest.mark.parametrize("pw", ["Secret123", "secret123", "SECRETPASS", "Ab1", "Abcdefg1", "Pass word1", "12345678A"])
def test_passwords(pw):
    got = run(pw + "\n")
    assert got == expected(pw), (
        f"For {pw!r} expected {expected(pw)}, got {got}. 'Has' checks need any(); 'only' needs all(). "
        "A space is not a letter or digit.")


def test_empty_password():
    got = run("\n")
    assert got == expected(""), (
        f"Empty password: expected {expected('')}, got {got}. all() of no characters is True, so the "
        "'Only letters and digits' line says yes (''.isalnum() would say no).")


def test_uses_any_and_all():
    assert calls("any") >= 1, "Use any() for the 'has' checks."
    assert calls("all") >= 1, "Use all() for the 'only letters and digits' check."
