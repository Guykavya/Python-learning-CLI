import pytest

from solution import SimpleDate


def test_plain_constructor():
    d = SimpleDate(2024, 3, 5)
    assert (d.year, d.month, d.day) == (2024, 3, 5), "SimpleDate(2024, 3, 5) should store year, month, day on self."


def test_from_iso():
    d = SimpleDate.from_iso("2024-03-05")
    assert isinstance(d, SimpleDate), "from_iso should return a SimpleDate object."
    assert (d.year, d.month, d.day) == (2024, 3, 5), "from_iso('2024-03-05') should give year 2024, month 3, day 5 as ints (use int())."


def test_iso_pads_with_zeros():
    assert SimpleDate(2024, 3, 5).iso() == "2024-03-05", "iso() must pad month and day to 2 digits: use :02d in the f-string."
    assert SimpleDate(987, 12, 31).iso() == "0987-12-31", "The year is padded to 4 digits: use :04d."


def test_round_trip():
    for text in ("2000-01-01", "1999-12-31", "2024-02-29"):
        assert SimpleDate.from_iso(text).iso() == text, f"from_iso({text!r}).iso() should give the same text back."


@pytest.mark.parametrize("year,leap", [(2024, True), (2000, True), (1900, False), (2023, False), (2400, True), (2100, False)])
def test_is_leap(year, leap):
    assert SimpleDate.is_leap(year) is leap, (
        f"is_leap({year}) should be {leap}. Rule: divisible by 4, except by 100, unless also by 400."
    )


def test_is_leap_is_a_staticmethod():
    assert isinstance(vars(SimpleDate)["is_leap"], staticmethod), "Decorate is_leap with @staticmethod: it needs no self and no cls."
    assert SimpleDate(2024, 1, 1).is_leap(2023) is False, "A staticmethod can also be called on an instance; it gets no self."


def test_from_iso_is_a_classmethod():
    assert isinstance(vars(SimpleDate)["from_iso"], classmethod), "Decorate from_iso with @classmethod so it receives the class as cls."


def test_from_iso_respects_subclass():
    class MyDate(SimpleDate):
        pass

    d = MyDate.from_iso("2024-03-05")
    assert type(d) is MyDate, "MyDate.from_iso(...) should return a MyDate. Use return cls(...), not SimpleDate(...)."


def test_february():
    assert SimpleDate(2024, 2, 29).day == 29, "2024 is a leap year, so February 29 exists."
    with pytest.raises(ValueError, match="bad day"):
        SimpleDate(2023, 2, 29)
    with pytest.raises(ValueError, match="bad day"):
        SimpleDate(1900, 2, 29)


def test_month_lengths():
    assert SimpleDate(2023, 1, 31).day == 31, "January has 31 days."
    with pytest.raises(ValueError, match="bad day"):
        SimpleDate(2023, 4, 31)
    with pytest.raises(ValueError, match="bad day"):
        SimpleDate(2023, 3, 0)


@pytest.mark.parametrize("month", [0, 13, -1])
def test_bad_month(month):
    with pytest.raises(ValueError, match="month must be 1-12"):
        SimpleDate(2024, month, 1)


def test_from_iso_checks_the_date_too():
    with pytest.raises(ValueError, match="month must be 1-12"):
        SimpleDate.from_iso("2024-13-01")
    with pytest.raises(ValueError, match="bad day"):
        SimpleDate.from_iso("2023-02-29")


@pytest.mark.parametrize("text", ["2024/03/05", "2024-3-5", "24-03-05", "2024-03", "2024-03-05-01", "abcd-ef-gh", "", "2024-03-5x"])
def test_from_iso_bad_format(text):
    with pytest.raises(ValueError, match="expected YYYY-MM-DD"):
        SimpleDate.from_iso(text)
