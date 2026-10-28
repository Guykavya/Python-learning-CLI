import pytest

from solution import count_by_length, group_by_first_letter


def test_group_basic():
    got = group_by_first_letter(["apple", "Bob", "avocado", "", "banana"])
    assert got == {"a": ["apple", "avocado"], "b": ["Bob", "banana"]}, (
        "Key = lower-case first letter, words kept as given and in input order, empty strings skipped."
    )


def test_group_returns_plain_dict():
    got = group_by_first_letter(["cat"])
    assert type(got) is dict, "Return dict(groups), not the defaultdict itself: a missing key must raise KeyError for the caller."
    with pytest.raises(KeyError):
        got["z"]


def test_group_case_of_key_only():
    got = group_by_first_letter(["Zed", "zoo", "ZIP"])
    assert list(got) == ["z"], "Only the KEY is lower-cased: 'Zed', 'zoo' and 'ZIP' all go under 'z'."
    assert got["z"] == ["Zed", "zoo", "ZIP"], "Keep the words exactly as given (do not lower-case them) and in input order."


def test_group_skips_empty():
    assert group_by_first_letter(["", "", "x"]) == {"x": ["x"]}, "'' has no first letter: skip it (''[0] would raise IndexError)."
    assert group_by_first_letter([]) == {}, "No words, no groups."


def test_group_no_empty_lists():
    got = group_by_first_letter(["a", "b"])
    assert all(got.values()), "Every group must have at least one word. Did a read like groups[key] create an empty list?"


def test_count_basic():
    assert count_by_length(["hi", "yo", "hey"]) == {2: 2, 3: 1}, "Count how many words have each length: two of length 2, one of length 3."


def test_count_includes_empty():
    assert count_by_length(["", "a", ""]) == {0: 2, 1: 1}, "Empty strings count too, under length 0."


def test_count_returns_plain_dict():
    got = count_by_length(["abc"])
    assert type(got) is dict, "Return dict(counts), not the defaultdict."
    with pytest.raises(KeyError):
        got[99]
    assert count_by_length([]) == {}, "No words: an empty dict."
