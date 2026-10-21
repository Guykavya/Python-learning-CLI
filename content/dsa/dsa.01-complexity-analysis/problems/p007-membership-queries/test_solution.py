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


def ask(members, queries, timeout=10):
    text = f"{len(members)}\n" + " ".join(map(str, members)) + f"\n{len(queries)}\n"
    text += "".join(f"{x}\n" for x in queries)
    return run(text, timeout=timeout)


def test_example():
    got = ask([17, 3, 42, 8], [42, 5, 17])
    assert got == ["YES", "NO", "YES"], f"The example: expected YES, NO, YES, got {got}."


def test_repeated_members_and_queries():
    got = ask([5, 5, 5], [5, 6, 5])
    assert got == ["YES", "NO", "YES"], (
        f"Members 5 5 5, queries 5 6 5: expected YES, NO, YES, got {got}. "
        "Repeated members and repeated questions must each get an answer line.")


def test_one_line_per_query():
    got = ask([1], [1, 2, 3, 1])
    assert got == ["YES", "NO", "NO", "YES"], (
        f"Expected one answer line per query (4 lines), got {got}.")


def test_large_mostly_missing():
    rng = random.Random(7)
    members = rng.sample(range(1, 10**9, 2), 100000)       # odd numbers only
    queries = [rng.randrange(2, 10**9, 2) for _ in range(99990)] + members[:10]
    got = ask(members, queries, timeout=6)
    expected = ["NO"] * 99990 + ["YES"] * 10
    assert got == expected, (
        "100000 members and 100000 queries, almost all missing: wrong answers or too slow. "
        "A missing number makes `x in list` look at all 100000 members, every time. "
        "Convert the members to a set once, before the queries.")
