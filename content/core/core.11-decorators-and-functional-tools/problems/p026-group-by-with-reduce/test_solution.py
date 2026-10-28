import copy

from solution import count_by, group_by, merge_counts


def first_letter(word):
    return word[0]


def parity(n):
    return "even" if n % 2 == 0 else "odd"


def test_group_by():
    words = ["apple", "bee", "avocado", "cat"]
    assert group_by(words, first_letter) == {"a": ["apple", "avocado"], "b": ["bee"], "c": ["cat"]}, (
        "Each key maps to a list of its items, in the original order."
    )
    assert list(group_by(words, first_letter)) == ["a", "b", "c"], "Keys appear in the order they are first seen."


def test_group_by_empty_and_fresh():
    assert group_by([], first_letter) == {}, "No items, no groups."
    first = group_by(["ab"], first_letter)
    second = group_by(["ac"], first_letter)
    assert second == {"a": ["ac"]}, (
        "The second call saw items from the first call. Start reduce from a NEW {} each call, "
        "not from a dict stored outside the function."
    )
    assert first == {"a": ["ab"]}, "The result of the first call must not change later."


def test_group_by_does_not_mutate_input():
    items = [[1], [2], [1]]
    snapshot = copy.deepcopy(items)
    groups = group_by(items, lambda x: x[0])
    assert items == snapshot, "Do not change the items."
    assert groups == {1: [[1], [1]], 2: [[2]]}


def test_count_by():
    assert count_by([3, 8, 5, 6, 1], parity) == {"odd": 3, "even": 2}, "Count how many items fall under each key."
    assert list(count_by([3, 8, 5], parity)) == ["odd", "even"], "Keys in first-seen order."
    assert count_by([], parity) == {}, "No items, empty dict."
    assert count_by(["x"], len) == {1: 1}


def test_merge_counts():
    a = {"a": 2, "b": 1}
    b = {"b": 5, "c": 1}
    assert merge_counts(a, b) == {"a": 2, "b": 6, "c": 1}, "Add the counts of keys that appear in both dicts."
    assert list(merge_counts(a, b)) == ["a", "b", "c"], "Keys in first-seen order."
    assert merge_counts() == {}, "No dicts at all gives {}: give reduce a start value."
    assert merge_counts({"z": 3}) == {"z": 3}


def test_merge_counts_does_not_mutate():
    a = {"a": 2, "b": 1}
    b = {"b": 5}
    merged = merge_counts(a, b)
    assert a == {"a": 2, "b": 1} and b == {"b": 5}, (
        "merge_counts changed one of its arguments. Copy before adding: dict(total) or {**total}."
    )
    assert merged is not a, "Return a new dict, not the first argument."
    merged["a"] = 100
    assert a["a"] == 2, "The result must be a separate dict from the arguments."
