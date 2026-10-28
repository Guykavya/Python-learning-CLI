from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pytest

from solution import is_aware, same_instant, to_utc, utc_to_local

UTC = timezone.utc


@pytest.fixture(autouse=True)
def require_tzdata():
    try:
        ZoneInfo("Europe/London")
    except ZoneInfoNotFoundError:
        pytest.fail("No time-zone data: run `.venv/Scripts/python -m pip install tzdata` (Windows) and try again.", pytrace=False)


def check_utc(got, expected_naive, why):
    assert isinstance(got, datetime), f"Return a datetime. {why}"
    assert got.utcoffset() == timedelta(0), f"The result must be in UTC (offset 0), not still in the local zone. {why}"
    assert got.replace(tzinfo=None) == expected_naive, f"Expected {expected_naive} UTC, got {got}. {why}"


def test_is_aware():
    assert is_aware(datetime(2025, 1, 1, tzinfo=UTC)), "tzinfo=UTC makes it aware."
    assert is_aware(datetime(2025, 1, 1, tzinfo=ZoneInfo("Asia/Kolkata"))), "A ZoneInfo makes it aware."
    assert not is_aware(datetime(2025, 1, 1)), "No tzinfo: naive."


def test_to_utc_kolkata():
    got = to_utc(datetime(2025, 3, 14, 9, 30), "Asia/Kolkata")
    check_utc(got, datetime(2025, 3, 14, 4, 0), "India is UTC+5:30 all year.")


def test_to_utc_london_winter_and_summer():
    check_utc(to_utc(datetime(2025, 1, 15, 12, 0), "Europe/London"), datetime(2025, 1, 15, 12, 0),
              "London is on GMT (UTC+0) in January.")
    check_utc(to_utc(datetime(2025, 7, 15, 12, 0), "Europe/London"), datetime(2025, 7, 15, 11, 0),
              "London is on BST (UTC+1) in July: 12:00 local is 11:00 UTC. A fixed offset cannot know this; ZoneInfo does.")


def test_to_utc_new_york():
    check_utc(to_utc(datetime(2025, 7, 4, 9, 0), "America/New_York"), datetime(2025, 7, 4, 13, 0),
              "New York in July is EDT, UTC-4.")
    check_utc(to_utc(datetime(2024, 12, 25, 9, 0), "America/New_York"), datetime(2024, 12, 25, 14, 0),
              "New York in December is EST, UTC-5.")


def test_to_utc_does_not_use_machine_zone():
    results = {to_utc(datetime(2025, 6, 1, 12, 0), z).hour for z in ("Asia/Kolkata", "Europe/London", "America/New_York")}
    assert results == {6, 11, 16}, (
        "The same wall time in three zones must give three different UTC hours. "
        "Attach the zone with replace(tzinfo=ZoneInfo(zone)); naive.astimezone(...) assumes YOUR computer's zone."
    )


def test_to_utc_rejects_aware():
    with pytest.raises(ValueError):
        to_utc(datetime(2025, 1, 1, tzinfo=UTC), "Europe/London")


def test_utc_to_local():
    got = utc_to_local(datetime(2025, 7, 4, 13, 0, tzinfo=UTC), "America/New_York")
    assert got.replace(tzinfo=None) == datetime(2025, 7, 4, 9, 0), "13:00 UTC is 09:00 in New York in July (EDT)."
    assert getattr(got.tzinfo, "key", None) == "America/New_York", "The result's tzinfo must be ZoneInfo('America/New_York'): use astimezone, not replace."


def test_utc_to_local_across_dst_start():
    # In 2025 London's clocks jump from 01:00 GMT to 02:00 BST at 01:00 UTC on 30 March.
    before = utc_to_local(datetime(2025, 3, 30, 0, 30, tzinfo=UTC), "Europe/London")
    after = utc_to_local(datetime(2025, 3, 30, 1, 30, tzinfo=UTC), "Europe/London")
    assert before.replace(tzinfo=None) == datetime(2025, 3, 30, 0, 30), "Before the change London is on GMT: 00:30 UTC is 00:30 local."
    assert after.replace(tzinfo=None) == datetime(2025, 3, 30, 2, 30), "After the change London is on BST: 01:30 UTC is 02:30 local."


def test_utc_to_local_accepts_any_aware():
    kolkata = datetime(2025, 3, 14, 9, 30, tzinfo=ZoneInfo("Asia/Kolkata"))
    got = utc_to_local(kolkata, "Europe/London")
    assert got.replace(tzinfo=None) == datetime(2025, 3, 14, 4, 0), "Any aware datetime can be converted: 09:30 IST is 04:00 GMT."


def test_utc_to_local_rejects_naive():
    with pytest.raises(ValueError):
        utc_to_local(datetime(2025, 7, 4, 13, 0), "Europe/London")


def test_round_trip():
    naive = datetime(2025, 11, 2, 18, 45)
    back = utc_to_local(to_utc(naive, "Asia/Kolkata"), "Asia/Kolkata")
    assert back.replace(tzinfo=None) == naive, "Local -> UTC -> the same zone gives the original wall time back."


def test_same_instant():
    london = datetime(2025, 7, 1, 13, 0, tzinfo=ZoneInfo("Europe/London"))
    new_york = datetime(2025, 7, 1, 8, 0, tzinfo=ZoneInfo("America/New_York"))
    kolkata = datetime(2025, 7, 1, 17, 30, tzinfo=ZoneInfo("Asia/Kolkata"))
    assert same_instant(london, new_york), "13:00 BST and 08:00 EDT are both 12:00 UTC."
    assert same_instant(london, kolkata), "13:00 BST and 17:30 IST are both 12:00 UTC."
    assert not same_instant(london, london + timedelta(minutes=1)), "One minute apart is not the same instant."


def test_same_instant_rejects_naive():
    with pytest.raises(ValueError):
        same_instant(datetime(2025, 7, 1, 12, 0), datetime(2025, 7, 1, 12, 0, tzinfo=UTC))
    with pytest.raises(ValueError):
        same_instant(datetime(2025, 7, 1, 12, 0), datetime(2025, 7, 1, 12, 0))
