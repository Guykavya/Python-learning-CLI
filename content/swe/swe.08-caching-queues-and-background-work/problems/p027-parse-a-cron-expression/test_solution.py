from datetime import datetime

import pytest

from solution import Cron, parse_field

FRI = datetime(2026, 11, 6, 9, 0)


@pytest.mark.parametrize("text, low, high, expected", [
    ("*", 0, 6, set(range(7))),
    ("5", 0, 59, {5}),
    ("1,15", 1, 31, {1, 15}),
    ("1-5", 0, 6, {1, 2, 3, 4, 5}),
    ("*/15", 0, 59, {0, 15, 30, 45}),
    ("0-30/10", 0, 59, {0, 10, 20, 30}),
    ("5/20", 0, 59, {5, 25, 45}),
    ("1-3,10,20-21", 1, 31, {1, 2, 3, 10, 20, 21}),
])
def test_parse_field(text, low, high, expected):
    assert parse_field(text, low, high) == expected, f"parse_field({text!r}, {low}, {high}) should be {sorted(expected)}"


@pytest.mark.parametrize("text", ["60", "5-1", "*/0", "", "1,,2", "x", "-1", "1-"])
def test_parse_field_errors_name_the_field(text):
    with pytest.raises(ValueError) as info:
        parse_field(text, 0, 59, "minute")
    assert "minute" in str(info.value), f"The error for {text!r} must name the field ('minute'); got {info.value}"


@pytest.mark.parametrize("expr, field", [
    ("0 25 * * *", "hour"), ("61 * * * *", "minute"), ("0 0 32 * *", "day"),
    ("0 0 * 13 *", "month"), ("0 0 * * 7", "weekday"),
])
def test_cron_error_names_field(expr, field):
    with pytest.raises(ValueError) as info:
        Cron(expr)
    assert field in str(info.value), f"Cron({expr!r}) must raise ValueError naming '{field}'; got {info.value}"


@pytest.mark.parametrize("expr", ["* * * *", "* * * * * *", ""])
def test_cron_needs_five_fields(expr):
    with pytest.raises(ValueError):
        Cron(expr)


@pytest.mark.parametrize("expr, expected", [
    ("*/15 * * * *", datetime(2026, 11, 6, 9, 15)),
    ("0 9 * * 1-5", datetime(2026, 11, 9, 9, 0)),
    ("30 2 1 * *", datetime(2026, 12, 1, 2, 30)),
    ("0 0 29 2 *", datetime(2028, 2, 29, 0, 0)),
    ("0 8 13 * 5", datetime(2026, 11, 13, 8, 0)),
    ("0 12 20 * 1", datetime(2026, 11, 9, 12, 0)),
    ("0 9 * * 0", datetime(2026, 11, 8, 9, 0)),
])
def test_next_after(expr, expected):
    got = Cron(expr).next_after(FRI)
    assert got == expected, f"{expr!r} after Fri 2026-11-06 09:00 should be {expected:%a %Y-%m-%d %H:%M}, got {got}"


def test_strictly_after():
    assert Cron("0 9 * * *").next_after(FRI) == datetime(2026, 11, 7, 9, 0), \
        "09:00 itself is not 'after' 09:00: the next run is tomorrow."


def test_seconds_are_ignored():
    assert Cron("* * * * *").next_after(datetime(2026, 11, 6, 9, 0, 30)) == datetime(2026, 11, 6, 9, 1), \
        "Run times are whole minutes: after 09:00:30 comes 09:01:00."


def test_day_or_weekday_rule():
    c = Cron("0 0 1 * 1")                                  # the 1st, OR any Monday
    runs = list(c.between(datetime(2026, 11, 30, 0, 0), datetime(2026, 12, 15, 0, 0)))
    assert runs == [datetime(2026, 12, 1), datetime(2026, 12, 7), datetime(2026, 12, 14)], \
        f"When both day fields are restricted, either may match (the 1st or a Monday); got {runs}"


def test_only_weekday_restricted():
    c = Cron("0 0 * * 6")                                  # Saturdays only: the * day field must not make every day match
    assert c.next_after(FRI) == datetime(2026, 11, 7), "With day-of-month '*', only the weekday decides."


def test_between():
    times = list(Cron("*/15 * * * *").between(datetime(2026, 11, 6, 10, 0), datetime(2026, 11, 6, 11, 0)))
    assert [f"{t:%H:%M}" for t in times] == ["10:15", "10:30", "10:45", "11:00"], \
        "between(start, end) yields start < t <= end: 10:00 excluded, 11:00 included."


def test_impossible_schedule():
    with pytest.raises(ValueError):
        Cron("0 0 31 2 *").next_after(FRI)                 # 31 February never happens
