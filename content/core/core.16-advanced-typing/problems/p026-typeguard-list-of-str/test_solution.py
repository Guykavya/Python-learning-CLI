from typing import TypeGuard, get_args, get_origin, get_type_hints

import pytest

from solution import is_int_dict, is_str_list, join_if_strings, sum_counts


def test_is_str_list_hints():
    h = get_type_hints(is_str_list)
    assert h["value"] == list[object], "is_str_list takes a list[object] (we do not know yet what is inside)."
    assert get_origin(h["return"]) is TypeGuard, "The return hint must be TypeGuard[...] (from typing import TypeGuard)."
    assert get_args(h["return"]) == (list[str],), "The guard says: if True, the value is a list[str]."


def test_is_int_dict_hints():
    h = get_type_hints(is_int_dict)
    assert h["value"] == dict[str, object], "is_int_dict takes a dict[str, object]."
    assert get_origin(h["return"]) is TypeGuard and get_args(h["return"]) == (dict[str, int],), (
        "is_int_dict returns TypeGuard[dict[str, int]]."
    )


def test_user_functions_hints():
    assert get_type_hints(join_if_strings) == {"items": list[object], "return": str}, (
        "join_if_strings(items: list[object]) -> str."
    )
    assert get_type_hints(sum_counts) == {"data": dict[str, object], "return": int}, (
        "sum_counts(data: dict[str, object]) -> int."
    )


def test_is_str_list_true_cases():
    assert is_str_list(["a", "b"]) is True, "Every item is a str: True."
    assert is_str_list([]) is True, "An empty list has no bad item: True (all([]) is True)."
    assert is_str_list([""]) is True, "The empty string is a str."


def test_is_str_list_false_cases():
    assert is_str_list(["a", 1]) is False, "One non-str item makes it False: check every item, not just the first."
    assert is_str_list([1, "a"]) is False, "A bad FIRST item is also False."
    assert is_str_list([None]) is False, "None is not a str."
    assert is_str_list([["a"]]) is False, "A nested list is not a str."
    assert is_str_list([b"a"]) is False, "bytes is not str."


def test_is_str_list_returns_a_real_bool():
    assert type(is_str_list(["a"])) is bool, "Return True/False (a bool), not a list or None."


def test_is_int_dict():
    assert is_int_dict({"a": 1, "b": 2}) is True, "All values are ints: True."
    assert is_int_dict({}) is True, "An empty dict has no bad value: True."
    assert is_int_dict({"a": 1, "b": "2"}) is False, "A str value makes it False."
    assert is_int_dict({"a": 1.5}) is False, "A float is not an int."
    assert is_int_dict({"a": True}) is False, "bool is a subclass of int, but a flag is not a count: reject it."
    assert is_int_dict({"a": None}) is False, "None is not an int."


def test_is_int_dict_checks_values_not_keys():
    assert is_int_dict({"x": 0}) is True, "0 is an int (do not test the value for truthiness)."


def test_join_if_strings():
    assert join_if_strings(["x", "y"]) == "x, y", "Join with ', '."
    assert join_if_strings(["x", 1]) == "", "Mixed list: ''."
    assert join_if_strings([]) == "", "Empty list joins to ''."
    assert join_if_strings(["solo"]) == "solo", "One item has no separator."


def test_sum_counts():
    assert sum_counts({"a": 1, "b": 2}) == 3, "Sum of the values."
    assert sum_counts({}) == 0, "Empty dict sums to 0."
    with pytest.raises(ValueError):
        sum_counts({"a": 1, "b": "2"})
    with pytest.raises(ValueError):
        sum_counts({"a": True})


def test_guard_functions_do_not_modify_input():
    items = ["a", "b"]
    is_str_list(items)
    assert items == ["a", "b"], "A guard only looks; it must not change its argument."
