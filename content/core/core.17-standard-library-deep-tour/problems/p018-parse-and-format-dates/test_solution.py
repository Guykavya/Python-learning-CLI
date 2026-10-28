import inspect
from datetime import date, datetime

import pytest

import solution
from solution import parse_log_stamp, parse_us_date, pretty, to_iso


def test_parse_log_stamp():
    got = parse_log_stamp("2025-03-14 09:05:30")
    assert got == datetime(2025, 3, 14, 9, 5, 30), "Format '%Y-%m-%d %H:%M:%S'. %M is minutes; %m is the month."
    assert parse_log_stamp("2024-12-31 23:59:59") == datetime(2024, 12, 31, 23, 59, 59), "%H is the 24-hour clock."


def test_parse_log_stamp_rejects_bad():
    for bad in ("2025-03-14", "14/03/2025 09:05:30", "2025-02-30 10:00:00", "2025-03-14 25:00:00"):
        with pytest.raises(ValueError):
            parse_log_stamp(bad)


def test_parse_us_date():
    got = parse_us_date("03/14/2025")
    assert got == date(2025, 3, 14), "US order is month/day/year: '%m/%d/%Y'."
    assert type(got) is date, "Return a date, not a datetime: call .date() on the parsed datetime."
    assert parse_us_date("12/01/2024") == date(2024, 12, 1), "12/01 is December 1st in US order, not January 12th."


def test_parse_us_date_rejects_day_month_order():
    with pytest.raises(ValueError):
        parse_us_date("14/03/2025")  # there is no month 14


def test_to_iso():
    assert to_iso(datetime(2025, 3, 14, 9, 5, 30)) == "2025-03-14T09:05:30", "isoformat() puts a 'T' between date and time."
    assert to_iso(datetime(2025, 1, 2)) == "2025-01-02T00:00:00", "Midnight still shows the time part."


def test_iso_round_trip():
    dt = datetime(2024, 2, 29, 23, 0, 1)
    assert datetime.fromisoformat(to_iso(dt)) == dt, "to_iso output must parse back to the same datetime."


def test_pretty():
    assert pretty(datetime(2025, 3, 14, 9, 5)) == "Fri 14 Mar 2025, 09:05", "Format: weekday, day, month, year, comma, HH:MM."
    assert pretty(datetime(2025, 3, 4, 9, 5)) == "Tue 4 Mar 2025, 09:05", "The day has no leading zero ('4', not '04'). Use dt.day."
    assert pretty(datetime(2024, 12, 1, 17, 0)) == "Sun 1 Dec 2024, 17:00", "Hours and minutes keep two digits."


def test_pretty_portable():
    src = inspect.getsource(solution.pretty)
    assert "%-d" not in src and "%#d" not in src, (
        "%-d only works on Linux/macOS and %#d only on Windows. Use dt.day to drop the leading zero on every system."
    )
