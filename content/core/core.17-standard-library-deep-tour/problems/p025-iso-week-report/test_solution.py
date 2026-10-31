from datetime import date

import pytest

from solution import week_key, week_start, weekly_report


@pytest.mark.parametrize("day, expected", [
    ("2024-01-01", "2024-W01"),
    ("2025-01-06", "2025-W02"),
    ("2024-03-06", "2024-W10"),
])
def test_week_key_ordinary(day, expected):
    assert week_key(date.fromisoformat(day)) == expected, (
        f"{day} is in ISO week {expected}. Use d.isocalendar() and pad the week to two digits (W01, not W1)."
    )


@pytest.mark.parametrize("day, expected, why", [
    ("2024-12-30", "2025-W01", "Monday 30 Dec 2024 starts ISO week 1 of 2025: use the ISO YEAR from isocalendar(), not d.year."),
    ("2025-01-05", "2025-W01", "Sunday 5 Jan 2025 is the last day of 2025-W01 (ISO weeks run Monday to Sunday)."),
    ("2024-12-29", "2024-W52", "Sunday 29 Dec 2024 is still in 2024-W52."),
    ("2027-01-01", "2026-W53", "Friday 1 Jan 2027 belongs to the last ISO week of 2026, which is week 53."),
    ("2023-01-01", "2022-W52", "Sunday 1 Jan 2023 belongs to 2022-W52."),
    ("2026-01-01", "2026-W01", "Thursday 1 Jan 2026: the week containing a year's first Thursday is week 1."),
])
def test_week_key_year_edges(day, expected, why):
    assert week_key(date.fromisoformat(day)) == expected, why + " strftime('%W') is NOT the ISO week."


def test_week_start():
    assert week_start("2025-W01") == date(2024, 12, 30), "The Monday of 2025-W01 is 30 Dec 2024. Use date.fromisocalendar(year, week, 1)."
    assert week_start("2024-W10") == date(2024, 3, 4), "The Monday of 2024-W10 is 4 March 2024."
    assert week_start("2026-W53") == date(2026, 12, 28), "2026 has 53 ISO weeks; its last Monday is 28 Dec 2026."


@pytest.mark.parametrize("bad", ["2024-W53", "2025-W00", "2025W01", "2025-W1", "abc", "25-W01"])
def test_week_start_rejects_bad_keys(bad):
    with pytest.raises(ValueError):
        week_start(bad)
    # 2024 has only 52 ISO weeks, and week 0 never exists: fromisocalendar raises ValueError for them


def test_week_key_round_trip():
    d = date(2024, 1, 1)
    for _ in range(800):
        key = week_key(d)
        monday = week_start(key)
        assert monday.weekday() == 0 and 0 <= (d - monday).days <= 6, (
            f"week_start(week_key({d})) must be the Monday on or before {d}; got {monday}."
        )
        d = date.fromordinal(d.toordinal() + 1)


def test_weekly_report():
    entries = [
        ("2025-01-02", 3.0),
        ("2024-12-30", 2.5),
        ("2024-12-29", 1.0),
        ("2024-12-30", 1.5),
        ("2025-01-05", 4.0),
    ]
    assert weekly_report(entries) == [
        "2024-W52 2024-12-23..2024-12-29: 1.0 h on 1 day",
        "2025-W01 2024-12-30..2025-01-05: 11.0 h on 3 days",
    ], (
        "Group by ISO week key, oldest week first. Hours are added up; 'days' counts DIFFERENT dates "
        "(30 Dec appears twice but is one day). The range is Monday..Sunday."
    )


def test_weekly_report_sorted_and_formatted():
    entries = [("2025-03-12", 7.3), ("2025-01-07", 2.0)]
    assert weekly_report(entries) == [
        "2025-W02 2025-01-06..2025-01-12: 2.0 h on 1 day",
        "2025-W11 2025-03-10..2025-03-16: 7.3 h on 1 day",
    ], "Sort by week key (the zero padding makes text order equal time order). Hours use one decimal: f'{h:.1f}'."


def test_weekly_report_empty():
    assert weekly_report([]) == [], "No entries: no lines."
