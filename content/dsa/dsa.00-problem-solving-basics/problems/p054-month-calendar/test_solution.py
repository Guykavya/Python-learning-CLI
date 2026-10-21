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
    # rstrip(), not strip(): strip() would remove the leading spaces of a first week line.
    return [line.rstrip() for line in r.stdout.rstrip().splitlines()]


def run_raw(stdin: str) -> str:
    r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return r.stdout

import ast
import calendar

import pytest

HEADER = "Mo Tu We Th Fr Sa Su"


def expected_lines(year, month):
    """Built with Python's calendar module, used only by the tests."""
    lines = [HEADER]
    for week in calendar.monthcalendar(year, month):
        cells = [f"{d:>2}" if d else "  " for d in week]
        lines.append(" ".join(cells).rstrip())
    return lines


def check(year, month, note=""):
    expected = expected_lines(year, month)
    got = run(f"{year}\n{month}\n")
    assert got[:1] == [HEADER], f"{year}-{month}: the first line must be exactly {HEADER!r}, got {got[:1]}."
    assert len(got) == len(expected), (
        f"{year}-{month}: expected {len(expected) - 1} week lines, got {len(got) - 1}. {note}\n"
        f"Expected:\n" + "\n".join(expected) + "\nGot:\n" + "\n".join(got))
    for e, g in zip(expected, got):
        assert g == e, (
            f"{year}-{month}: expected line {e!r}, got {g!r}. {note} Check the weekday of the 1st, "
            "the number of days, and that each cell is width 2 with single spaces between cells.\n"
            "Expected:\n" + "\n".join(expected) + "\nGot:\n" + "\n".join(got))


def test_may_2024_starts_wednesday():
    check(2024, 5, "May 2024 starts on a Wednesday: the first week line is 7 spaces then ' 1'.")


def test_feb_2024_leap():
    check(2024, 2, "2024 is a leap year, so February has 29 days.")


def test_feb_2023_not_leap():
    check(2023, 2, "2023 is not a leap year, so February has 28 days.")


def test_feb_2021_four_rows():
    check(2021, 2, "February 2021 starts on Monday and has 28 days: exactly 4 full rows, no empty line.")


def test_feb_1900_not_leap():
    check(1900, 2, "1900 is a century not divisible by 400, so it is NOT a leap year.")


def test_feb_2000_leap():
    check(2000, 2, "2000 is divisible by 400, so it IS a leap year.")


def test_starts_on_sunday_six_rows():
    check(2023, 10, "October 2023 starts on a Sunday: 6 blank cells, then 6 week lines in total.")
    check(2024, 9, "September 2024 starts on a Sunday and has 30 days.")


def test_jan_2000():
    check(2000, 1, "January uses months 13/14 of the PREVIOUS year in Zeller's formula.")


@pytest.mark.parametrize("year, month", [(9999, 12), (1583, 1), (2026, 3), (1999, 12), (2100, 2), (2024, 4)])
def test_more_months(year, month):
    check(year, month)


def test_no_trailing_spaces_and_no_empty_lines():
    out = run_raw("2023\n10\n")
    for line in out.splitlines():
        assert line == line.rstrip(), f"The line {line!r} ends with spaces. No line may have trailing spaces."
        assert line != "", "Do not print empty lines (for example after a week that ended exactly on Sunday)."


def test_no_imports():
    tree = ast.parse(SOLUTION.read_text())
    assert not any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree)), (
        "Do not import anything (no calendar or datetime). Compute the calendar yourself.")
