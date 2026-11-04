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

import random

def ask(rows, timeout=10):
    return run(f"{len(rows)}\n" + "\n".join(f"{n} {s}" for n, s in rows) + "\n", timeout=timeout)


def model(rows):
    return [f"{n} {s}" for n, s in sorted(rows, key=lambda r: (-r[1], r[0]))]


@pytest.mark.parametrize("rows, why", [
    ([("zoe", 90), ("ann", 85), ("bob", 90), ("cy", 70), ("dee", 85)], "the example"),
    ([("a", 5)], "one student"),
    ([("b", 1), ("a", 1), ("c", 1)], "all tied: names A to Z"),
    ([("a", 9), ("b", 100), ("c", 20)], "numbers, not strings: 100 > 20 > 9"),
    ([("m", 0), ("n", 10**9)], "extreme scores"),
])
def test_examples(rows, why):
    got = ask(rows)
    assert got == model(rows), f"Input {rows}: expected {model(rows)}, got {got} ({why}). Score high to low, then name A to Z."


def test_large():
    rng = random.Random(10)
    rows = [("".join(rng.choice("abcde") for _ in range(4)), rng.randint(0, 50)) for _ in range(100000)]
    assert ask(rows) == model(rows), "Wrong or too slow on 100000 students."
