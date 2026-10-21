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


def one(text):
    out = run(f"{text}\nend\n")
    assert len(out) == 1, f"One time line should print exactly one line, got {out}"
    return out[0]


@pytest.mark.parametrize("text, want", [
    ("9:05", "09:05:00 = 32700 s"),
    ("23:59:59", "23:59:59 = 86399 s"),
    ("0:00", "00:00:00 = 0 s"),
    ("00:00:01", "00:00:01 = 1 s"),
    ("12:30 am", "00:30:00 = 1800 s"),
    ("12:00 pm", "12:00:00 = 43200 s"),
    ("7:15:30 PM", "19:15:30 = 69330 s"),
    ("11:59:59 pm", "23:59:59 = 86399 s"),
    ("1:00 Am", "01:00:00 = 3600 s"),
])
def test_valid(text, want):
    assert one(text) == want, (
        f"{text!r} should give {want!r}. In 12-hour form, 12 am is hour 0 and 12 pm is hour 12 "
        "(hour % 12, then + 12 for pm).")


@pytest.mark.parametrize("text", [
    "24:00", "13:00 pm", "0:30 am", "9:5", "9:005", "9:60", "9:30:60", "123:00", "ab:cd",
    "9", "9:00:00:00", "9:00 xm", "9:00 am extra", "", "-1:00", ":30", "9:0a",
])
def test_invalid(text):
    assert one(text) == f"invalid: {text.strip()}".rstrip(), (
        f"{text!r} is not a valid time. Check the shape first (2 or 3 parts, optional am/pm), "
        "then digits, lengths and ranges.")


def test_several_lines():
    assert run("1:00\n  2:00 pm  \nnope\nend\n") == ["01:00:00 = 3600 s", "14:00:00 = 50400 s", "invalid: nope"], (
        "Process every line until end; strip spaces.")


def test_uses_match():
    assert has(ast.Match), "Use match/case to recognise the shapes."
    assert has(ast.MatchSequence), "Use sequence patterns such as case [h, m]:"
