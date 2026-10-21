import pytest

from solution import parse_time


@pytest.mark.parametrize("text, expected", [
    ("1:30", 90), ("0:05", 5), ("0:00", 0), ("12:00", 720), ("2:59", 179), ("100:00", 6000),
])
def test_valid_times(text, expected):
    assert parse_time(text) == expected, f"parse_time({text!r}) should be {expected}: hours * 60 + minutes."


def test_surrounding_spaces_ignored():
    assert parse_time("  1:30 ") == 90, "Use text.strip() before splitting."


@pytest.mark.parametrize("text", ["130", "1:30:00", "", "1::30"])
def test_wrong_shape(text):
    with pytest.raises(ValueError, match="H:MM"):
        parse_time(text)


@pytest.mark.parametrize("text", ["a:30", "1:xx", ":30", "1:"])
def test_not_whole_numbers(text):
    with pytest.raises(ValueError, match="whole numbers"):
        parse_time(text)


@pytest.mark.parametrize("text", ["1:60", "0:99", "1:-5"])
def test_minutes_out_of_range(text):
    with pytest.raises(ValueError, match="minutes"):
        parse_time(text)
