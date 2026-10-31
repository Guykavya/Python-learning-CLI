from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pytest

from solution import is_overdue, parse_local, shift_hours, to_utc_iso

NO_TZ = "No time-zone data: run `.venv/Scripts/python -m pip install tzdata` (Windows) and try again."


@pytest.fixture(autouse=True)
def _need_tz_data():
    try:
        ZoneInfo("Europe/London")
    except ZoneInfoNotFoundError:
        pytest.fail(NO_TZ, pytrace=False)


# ------------------------------------------------------------------ bug 1: parse_local
def test_parse_local_is_aware_in_the_right_zone():
    dt = parse_local("2024-07-01 09:00", "Asia/Kolkata")
    assert dt.tzinfo is not None, "parse_local must return an AWARE datetime: attach ZoneInfo(zone) to the parsed time."
    assert dt.tzinfo == ZoneInfo("Asia/Kolkata"), "Attach the zone itself (ZoneInfo(zone)), not a fixed offset."
    assert (dt.hour, dt.minute) == (9, 0), "Keep the wall-clock time: use replace(tzinfo=...), not astimezone()."
    assert dt.utcoffset() == timedelta(hours=5, minutes=30), "Kolkata is UTC+5:30."


def test_parse_local_offset_follows_dst():
    assert parse_local("2024-01-15 09:00", "Europe/London").utcoffset() == timedelta(0), "London in January: GMT, +0."
    assert parse_local("2024-07-15 09:00", "Europe/London").utcoffset() == timedelta(hours=1), (
        "London in July: BST, +1. A fixed timezone(timedelta(...)) offset cannot do this; ZoneInfo can."
    )


def test_parse_local_rejects_a_skipped_time():
    with pytest.raises(ValueError):
        parse_local("2024-03-31 01:30", "Europe/London")   # 01:00 GMT -> 02:00 BST
    with pytest.raises(ValueError):
        parse_local("2024-03-10 02:30", "America/New_York")  # 02:00 EST -> 03:00 EDT


def test_parse_local_repeated_time_is_the_first_one():
    dt = parse_local("2024-10-27 01:30", "Europe/London")  # 01:00-02:00 happens twice that night
    assert dt.utcoffset() == timedelta(hours=1), (
        "A repeated time means the first one (still BST, +1). That is fold=0, the default: do not raise for it."
    )


def test_parse_local_just_outside_the_gap_is_fine():
    assert parse_local("2024-03-31 00:59", "Europe/London").utcoffset() == timedelta(0), "00:59 exists (GMT)."
    assert parse_local("2024-03-31 02:00", "Europe/London").utcoffset() == timedelta(hours=1), "02:00 exists (BST)."


# ------------------------------------------------------------------ bug 2: to_utc_iso
@pytest.mark.parametrize("text, zone, expected", [
    ("2024-07-01 09:00", "Asia/Kolkata", "2024-07-01T03:30:00+00:00"),
    ("2024-01-15 12:00", "America/New_York", "2024-01-15T17:00:00+00:00"),
    ("2024-07-15 12:00", "America/New_York", "2024-07-15T16:00:00+00:00"),
    ("2024-07-01 09:00", "Europe/London", "2024-07-01T08:00:00+00:00"),
    ("2024-10-27 01:30", "Europe/London", "2024-10-27T00:30:00+00:00"),
    ("2025-01-01 00:00", "UTC", "2025-01-01T00:00:00+00:00"),
])
def test_to_utc_iso(text, zone, expected):
    assert to_utc_iso(text, zone) == expected, (
        f"{text} in {zone} is {expected} in UTC. Calling .astimezone() on a NAIVE datetime treats it as THIS "
        "computer's local time, so the answer changes from machine to machine. Make it aware first."
    )


# ------------------------------------------------------------------ bug 3: shift_hours
def test_shift_hours_normal_night():
    assert shift_hours("2024-06-01 22:00", "2024-06-02 06:00", "Europe/London") == 8.0, "An ordinary night shift is 8 hours."


def test_shift_hours_autumn_night_is_longer():
    assert shift_hours("2024-10-26 22:00", "2024-10-27 06:00", "Europe/London") == 9.0, (
        "On 27 Oct 2024 London repeats the hour 01:00-02:00, so the 22:00-06:00 shift is really 9 hours. "
        "Subtracting two aware datetimes with the SAME zone still compares wall clocks: convert both to UTC first."
    )
    assert shift_hours("2024-11-02 22:00", "2024-11-03 06:00", "America/New_York") == 9.0, (
        "New York falls back on 3 Nov 2024: 9 real hours."
    )


def test_shift_hours_spring_night_is_shorter():
    assert shift_hours("2024-03-30 22:00", "2024-03-31 06:00", "Europe/London") == 7.0, (
        "On 31 Mar 2024 London skips 01:00-02:00, so the night shift is only 7 hours."
    )


def test_shift_hours_returns_float():
    got = shift_hours("2024-06-01 09:00", "2024-06-01 13:30", "Asia/Kolkata")
    assert isinstance(got, float) and got == 4.5, "4 hours 30 minutes is 4.5 hours, as a float."


# ------------------------------------------------------------------ bug 4: is_overdue
def test_is_overdue_with_a_non_utc_now():
    due = "2024-05-01T12:00:00+00:00"
    kolkata = ZoneInfo("Asia/Kolkata")
    assert is_overdue(due, datetime(2024, 5, 1, 15, 0, tzinfo=kolkata)) is False, (
        "15:00 in Kolkata is 09:30 UTC, before 12:00 UTC: not overdue. Dropping tzinfo compares 15:00 with 12:00."
    )
    assert is_overdue(due, datetime(2024, 5, 1, 18, 0, tzinfo=kolkata)) is True, "18:00 IST is 12:30 UTC: overdue."
    ny = ZoneInfo("America/New_York")
    assert is_overdue(due, datetime(2024, 5, 1, 8, 30, tzinfo=ny)) is True, (
        "08:30 in New York (EDT) is 12:30 UTC: overdue. Compare aware datetimes directly; Python converts both to UTC."
    )
    assert is_overdue(due, datetime(2024, 5, 1, 7, 30, tzinfo=ny)) is False, "07:30 EDT is 11:30 UTC: not yet."


def test_is_overdue_due_in_another_offset():
    now = datetime(2024, 5, 1, 4, 0, tzinfo=timezone.utc)
    assert is_overdue("2024-05-01T09:00:00+05:30", now) is True, "09:00+05:30 is 03:30 UTC; at 04:00 UTC it is overdue."
    assert is_overdue("2024-05-01T10:00:00+05:30", now) is False, "10:00+05:30 is 04:30 UTC: not yet."


def test_is_overdue_exact_moment():
    now = datetime(2024, 5, 1, 12, 0, tzinfo=timezone.utc)
    assert is_overdue("2024-05-01T12:00:00+00:00", now) is False, "At exactly the due moment it is not yet overdue (after, not at)."


def test_is_overdue_rejects_naive():
    with pytest.raises(ValueError):
        is_overdue("2024-05-01T12:00:00+00:00", datetime(2024, 5, 1, 15, 0))
    with pytest.raises(ValueError):
        is_overdue("2024-05-01T12:00:00", datetime(2024, 5, 1, 15, 0, tzinfo=timezone.utc))
