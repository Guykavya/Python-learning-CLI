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
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import ast
import datetime
import random

import pytest

NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def ask(d, m, y):
    return run(f"{d}\n{m}\n{y}\n")


@pytest.mark.parametrize("d, m, y, expected, why", [
    (1, 1, 2000, "Saturday", "a well-known date"),
    (1, 1, 1970, "Thursday", "a well-known date"),
    (29, 2, 2024, "Thursday", "2024 is a leap year, so 29 February exists"),
    (29, 2, 2000, "Tuesday", "2000 is divisible by 400, so it IS a leap year"),
    (31, 12, 9999, "Friday", "the last allowed date"),
    (1, 1, 1583, "Saturday", "the first allowed year; January uses the previous year (1582) in Zeller"),
    (28, 2, 2023, "Tuesday", "the last day of February in a normal year"),
    (1, 3, 2024, "Friday", "March is month 3, no year adjustment"),
])
def test_known_dates(d, m, y, expected, why):
    got = ask(d, m, y)
    assert got == [expected], (
        f"Input {d} {m} {y}: expected {expected!r}, got {got}. Note: {why}. "
        "If only January/February dates are wrong, check you moved them to months 13/14 of the previous year.")


@pytest.mark.parametrize("d, m, y, why", [
    (29, 2, 2023, "2023 is not a leap year"),
    (29, 2, 1900, "1900 is divisible by 100 but not by 400, so it is not a leap year"),
    (30, 2, 2024, "February never has 30 days"),
    (31, 4, 2024, "April has 30 days"),
    (31, 11, 2024, "November has 30 days"),
    (0, 5, 2024, "there is no day 0"),
    (-3, 5, 2024, "days cannot be negative"),
    (32, 1, 2024, "January has 31 days"),
    (15, 13, 2024, "there is no month 13"),
    (15, 0, 2024, "there is no month 0"),
])
def test_invalid_dates(d, m, y, why):
    got = ask(d, m, y)
    assert got == ["invalid date"], f"Input {d} {m} {y}: expected 'invalid date' ({why}), got {got}."


def test_last_days_are_valid():
    for d, m, y in [(31, 1, 2023), (30, 4, 2023), (31, 7, 2023), (31, 8, 2023)]:
        expected = NAMES[datetime.date(y, m, d).weekday()]
        got = ask(d, m, y)
        assert got == [expected], (
            f"Input {d} {m} {y}: expected {expected!r}, got {got}. Check your month lengths "
            "(July and August both have 31 days).")


def test_random_dates_match_datetime():
    rng = random.Random(47)
    lo = datetime.date(1583, 1, 1).toordinal()
    hi = datetime.date(9999, 12, 31).toordinal()
    for _ in range(25):
        dt = datetime.date.fromordinal(rng.randint(lo, hi))
        expected = NAMES[dt.weekday()]
        got = ask(dt.day, dt.month, dt.year)
        assert got == [expected], (
            f"Input {dt.day} {dt.month} {dt.year}: expected {expected!r}, got {got}. "
            "Check the brackets in the formula and that you use // (not /) everywhere.")


def test_no_imports():
    tree = ast.parse(SOLUTION.read_text())
    assert not any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree)), (
        "Do not import anything (no datetime or calendar). The point is to compute it yourself.")
