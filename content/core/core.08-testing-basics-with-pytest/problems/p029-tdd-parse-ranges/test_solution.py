import pytest

from solution import parse_ranges


def test_1_single_number():
    assert parse_ranges("5") == [5], "A single number gives a list with that number."


def test_2_simple_range_includes_both_ends():
    assert parse_ranges("1-3") == [1, 2, 3], "'1-3' includes 1 and 3. Use range(low, high + 1)."


def test_3_several_pieces():
    assert parse_ranges("1-3,5,7-9") == [1, 2, 3, 5, 7, 8, 9], "Split on commas and expand every piece."


def test_4_spaces_ignored():
    assert parse_ranges(" 2 , 4 - 6 ") == [2, 4, 5, 6], "Strip spaces around pieces and around the numbers."


def test_5_sorted_and_no_duplicates():
    assert parse_ranges("3,1-3") == [1, 2, 3], "Duplicates are removed (use a set)."
    assert parse_ranges("9,2,5") == [2, 5, 9], "The result is sorted, whatever order the user typed."


def test_6_blank_text_is_empty():
    assert parse_ranges("") == [], "Blank text gives an empty list."
    assert parse_ranges("   ") == [], "Only spaces: also an empty list."


def test_one_page_range():
    assert parse_ranges("4-4") == [4], "A range with equal ends is one number."


@pytest.mark.parametrize("text", ["a", "1-", "-3", "1-2-3", "1,,2", "1.5", "1-b", "1,x"])
def test_7_invalid_pieces(text):
    with pytest.raises(ValueError, match="invalid"):
        parse_ranges(text)


@pytest.mark.parametrize("text", ["5-3", "10-1", "1,9-2"])
def test_8_reversed_ranges(text):
    with pytest.raises(ValueError, match="reversed"):
        parse_ranges(text)
