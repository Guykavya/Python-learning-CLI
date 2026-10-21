import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import pytest


@pytest.mark.parametrize("a, b, c, exact, close", [
    ("0.1", "0.2", "0.3", "False", "True"),
    ("1", "2", "3", "True", "True"),
    ("1", "2", "3.1", "False", "False"),
    ("0.5", "0.25", "0.75", "True", "True"),
    ("1e-12", "0", "0", "False", "True"),
    ("1e16", "1", "1e16", "True", "True"),
])
def test_cases(a, b, c, exact, close):
    out = run(f"{a}\n{b}\n{c}\n")
    assert out[0] == f"Exact: {exact}", f"For {a} + {b} == {c} Python gives {exact}."
    assert out[1] == f"Close: {close}", (
        f"For {a} + {b} vs {c}, close should be {close}. "
        "Use math.isclose(a + b, c, abs_tol=1e-9); without abs_tol nothing is close to 0 except 0.")
