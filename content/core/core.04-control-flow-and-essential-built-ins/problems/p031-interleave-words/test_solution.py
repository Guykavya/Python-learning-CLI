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

import pytest


def weave(a, b):
    out = "".join(x + y for x, y in zip(a, b))
    return out + a[len(b):] + b[len(a):]


@pytest.mark.parametrize("a, b", [("abc", "123"), ("abc", "12345"), ("hello", "XY"), ("x", "y"), ("", "abc"), ("abc", ""), ("a b", "-_-_-")])
def test_weave(a, b):
    want = weave(a, b)
    got = run(f"{a}\n{b}\n")
    assert got == [want], (
        f"First {a!r}, second {b!r}: expected [{want!r}], got {got}. zip stops at the shorter line, "
        "so add what is left of the longer line afterwards.")


def test_both_empty():
    assert run("\n\n") == ["(empty)"], "Both lines empty: print (empty)."
