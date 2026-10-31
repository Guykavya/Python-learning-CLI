from datetime import date, timedelta

import pytest

from solution import add_business_days, age_on, days_between, format_duration


def test_days_between():
    assert days_between(date(2025, 2, 1), date(2025, 3, 1)) == 28, "February 2025 has 28 days."
    assert days_between(date(2024, 2, 1), date(2024, 3, 1)) == 29, "2024 is a leap year: February has 29 days."
    assert days_between(date(2025, 3, 1), date(2025, 2, 1)) == 28, "The order does not matter: use abs()."
    assert days_between(date(2025, 5, 5), date(2025, 5, 5)) == 0, "Same day: 0."
    assert days_between(date(2024, 1, 1), date(2025, 1, 1)) == 366, "A leap year has 366 days. Never assume 365."


def test_business_days_forward():
    fri = date(2025, 3, 14)
    assert fri.weekday() == 4, "(sanity check: 14 March 2025 is a Friday)"
    assert add_business_days(fri, 1) == date(2025, 3, 17), "Friday + 1 working day is Monday: skip Saturday and Sunday."
    assert add_business_days(fri, 5) == date(2025, 3, 21), "Friday + 5 working days is the next Friday."
    assert add_business_days(date(2025, 3, 10), 3) == date(2025, 3, 13), "Monday + 3 is Thursday (no weekend in between)."


def test_business_days_from_weekend():
    sat = date(2025, 3, 15)
    assert add_business_days(sat, 1) == date(2025, 3, 17), "From Saturday, 1 working day forward is Monday."
    assert add_business_days(sat, 0) == sat, "n = 0 returns start unchanged, even on a weekend."


def test_business_days_backward():
    mon = date(2025, 3, 17)
    assert add_business_days(mon, -1) == date(2025, 3, 14), "Monday - 1 working day is the Friday before."
    assert add_business_days(mon, -6) == date(2025, 3, 7), "Monday 17 March - 6 working days counts 14, 13, 12, 11, 10, then skips the weekend: Friday 7 March."
    assert add_business_days(date(2025, 3, 16), -1) == date(2025, 3, 14), "From Sunday, 1 working day back is Friday."


def test_business_days_long_and_year_end():
    assert add_business_days(date(2024, 12, 31), 1) == date(2025, 1, 1), "Tuesday 31 Dec 2024 + 1 is Wednesday 1 Jan 2025 (no holidays here)."
    assert add_business_days(date(2025, 1, 6), 20) == date(2025, 2, 3), "20 working days = exactly 4 weeks from a Monday."


def test_age_on():
    assert age_on(date(2000, 6, 15), date(2025, 6, 14)) == 24, "The day before the birthday: still 24."
    assert age_on(date(2000, 6, 15), date(2025, 6, 15)) == 25, "On the birthday: 25."
    assert age_on(date(2000, 6, 15), date(2025, 1, 1)) == 24, "Earlier in the year: the birthday has not come yet."
    assert age_on(date(2000, 1, 1), date(2000, 12, 31)) == 0, "Before the first birthday: 0."


def test_age_not_by_days():
    assert age_on(date(2004, 3, 1), date(2025, 2, 28)) == 20, (
        "Do not use (today - birth).days // 365: leap days make it wrong near birthdays. Compare (month, day)."
    )
    assert age_on(date(2004, 3, 1), date(2025, 3, 1)) == 21, "On 1 March the birthday has arrived: 21."


def test_age_leap_birthday():
    leap = date(2004, 2, 29)
    assert age_on(leap, date(2025, 2, 28)) == 20, "Born 29 Feb: in 2025 the birthday counts on 1 March, so on 28 Feb still 20."
    assert age_on(leap, date(2025, 3, 1)) == 21, "Born 29 Feb: 21 on 1 March 2025."
    assert age_on(leap, date(2024, 2, 29)) == 20, "In a leap year the birthday is 29 Feb itself."


def test_format_duration():
    assert format_duration(timedelta(hours=26, seconds=5)) == "1d 02:00:05", "26 hours = 1 day + 2 hours. td.seconds holds only the part below one day."
    assert format_duration(timedelta(seconds=59)) == "0d 00:00:59", "Two digits for hours, minutes and seconds: use :02d."
    assert format_duration(timedelta(days=3, minutes=61)) == "3d 01:01:00", "61 minutes = 1 hour 1 minute."
    assert format_duration(timedelta(0)) == "0d 00:00:00", "Zero duration."


def test_format_duration_drops_microseconds():
    assert format_duration(timedelta(seconds=1, microseconds=999_999)) == "0d 00:00:01", "Microseconds are dropped, not rounded."


def test_format_duration_negative():
    with pytest.raises(ValueError):
        format_duration(timedelta(seconds=-1))
