import pytest

from target import average


def test_simple_list():
    assert average([2, 4, 6]) == 4, "The mean of 2, 4 and 6 is 4."


def test_result_is_not_rounded_down():
    assert average([1, 2]) == 1.5, "Use / (true division), not //."


def test_single_number():
    assert average([7]) == 7, "The mean of one number is that number."


def test_last_item_counts():
    assert average([0, 0, 9]) == 3, "Every item must be included, including the last."


def test_empty_list_raises_value_error():
    with pytest.raises(ValueError, match="empty"):
        average([])
