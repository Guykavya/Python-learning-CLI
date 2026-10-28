from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pytest

from solution import common_hours, show_in_zones

NO_TZ = "No time-zone data: run `.venv/Scripts/python -m pip install tzdata` (Windows) and try again."


@pytest.fixture(autouse=True)
def _need_tz_data():
    try:
        ZoneInfo("Europe/London")
    except ZoneInfoNotFoundError:
        pytest.fail(NO_TZ, pytrace=False)


UTC = timezone.utc
LON_NY = ["Europe/London", "America/New_York"]


def hours(slots):
    return [s.hour for s in slots]


# ------------------------------------------------------------------ show_in_zones
def test_show_in_zones_basic():
    when = datetime(2024, 3, 15, 14, 0, tzinfo=UTC)
    got = show_in_zones(when, ["Europe/London", "America/New_York", "Asia/Kolkata", "UTC"])
    assert got == [
        "Europe/London: 2024-03-15 14:00 GMT",
        "America/New_York: 2024-03-15 10:00 EDT",
        "Asia/Kolkata: 2024-03-15 19:30 IST",
        "UTC: 2024-03-15 14:00 UTC",
    ], (
        "Convert with when.astimezone(ZoneInfo(name)) and format as 'Zone: YYYY-MM-DD HH:MM ABBR'. "
        "On 15 March 2024 New York is already on EDT (-4) but London is still on GMT."
    )


def test_show_in_zones_date_can_change():
    when = datetime(2024, 1, 31, 20, 0, tzinfo=UTC)
    assert show_in_zones(when, ["Asia/Kolkata", "America/New_York"]) == [
        "Asia/Kolkata: 2024-02-01 01:30 IST",
        "America/New_York: 2024-01-31 15:00 EST",
    ], "Print the LOCAL date too: 20:00 UTC on 31 Jan is already 1 Feb in Kolkata. Keep the zones in the order given."


def test_show_in_zones_accepts_any_aware_input():
    when = datetime(2024, 7, 1, 9, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
    assert show_in_zones(when, ["Europe/London"]) == ["Europe/London: 2024-07-01 04:30 BST"], (
        "The input may be aware in any zone, not only UTC. astimezone() handles that; in July London is on BST (+1)."
    )


def test_show_in_zones_rejects_naive():
    with pytest.raises(ValueError):
        show_in_zones(datetime(2024, 3, 15, 14, 0), ["UTC"])
    # a naive datetime would be read as THIS computer's local time by astimezone(): a silent bug


def test_show_in_zones_empty():
    assert show_in_zones(datetime(2024, 3, 15, tzinfo=UTC), []) == [], "No zones: an empty list."


# ------------------------------------------------------------------ common_hours
def test_common_hours_returns_aware_utc_slots():
    slots = common_hours(date(2024, 1, 15), LON_NY)
    assert slots, "London and New York do overlap on 15 Jan 2024 (14:00-17:00 UTC)."
    for s in slots:
        assert s.tzinfo is not None and s.utcoffset() == timedelta(0), (
            "Return aware datetimes in UTC (tzinfo=timezone.utc), not naive ones and not local times."
        )
        assert (s.minute, s.second, s.date()) == (0, 0, date(2024, 1, 15)), "Each slot starts on the hour, on the given UTC day."
    assert slots == sorted(slots), "Return the slots in time order."


def test_common_hours_winter():
    assert hours(common_hours(date(2024, 1, 15), LON_NY)) == [14, 15, 16], (
        "In January London is UTC+0 and New York UTC-5: London works 09-17 UTC, New York 14-22 UTC. "
        "A slot must END by 17:00 local, so 16:00 UTC is the last one."
    )


def test_common_hours_between_the_two_dst_starts():
    assert hours(common_hours(date(2024, 3, 15), LON_NY)) == [13, 14, 15, 16], (
        "On 15 March 2024 New York is already on EDT (UTC-4) but London is still on GMT: the overlap is one hour "
        "longer for these weeks. Fixed offsets (like 'New York is always -5') get this wrong."
    )


def test_common_hours_summer():
    assert hours(common_hours(date(2024, 7, 15), LON_NY)) == [13, 14, 15], (
        "In July both are on summer time: London UTC+1 (08-16 UTC), New York UTC-4 (13-21 UTC)."
    )


def test_common_hours_half_hour_zone():
    assert hours(common_hours(date(2025, 6, 2), ["Asia/Kolkata"])) == [4, 5, 6, 7, 8, 9, 10], (
        "Kolkata is UTC+5:30. The slot 03:00 UTC starts at 08:30 local (too early) and 11:00 UTC ends at 17:30 "
        "local (too late). Check the minutes too, not only local.hour."
    )
    assert hours(common_hours(date(2024, 1, 15), ["Europe/London", "Asia/Kolkata"])) == [9, 10], (
        "London in winter (09-17 UTC) and Kolkata (04-11 UTC) share only 09:00 and 10:00 UTC."
    )
    assert hours(common_hours(date(2024, 7, 15), ["Europe/London", "Asia/Kolkata"])) == [8, 9, 10], (
        "In summer London starts at 08:00 UTC, so one more shared hour with Kolkata."
    )


def test_common_hours_no_overlap():
    assert common_hours(date(2024, 7, 15), ["America/New_York", "Asia/Kolkata"]) == [], (
        "New York and Kolkata office hours do not overlap at all: return an empty list."
    )


def test_common_hours_custom_window():
    got = common_hours(date(2024, 1, 15), LON_NY, start_hour=8, end_hour=18)
    assert [s.isoformat() for s in got] == [f"2024-01-15T{h}:00:00+00:00" for h in (13, 14, 15, 16, 17)], (
        "Use start_hour and end_hour instead of the fixed 9 and 17."
    )


def test_common_hours_utc_only():
    assert hours(common_hours(date(2025, 6, 2), ["UTC"])) == list(range(9, 17)), (
        "With only UTC, the slots are 09:00 to 16:00 (the 16:00 slot ends at 17:00)."
    )
