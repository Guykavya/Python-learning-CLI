import pytest

from solution import call_method, get_path, pick

ROWS = [("ann", 31, "Pune"), ("bo", 25, "Delhi"), ("cy", 40, "Goa")]


def test_pick_many():
    assert pick(ROWS, 2, 0) == [("Pune", "ann"), ("Delhi", "bo"), ("Goa", "cy")], "Return the items in the order of the indexes, as tuples."


def test_pick_one_gives_tuples():
    assert pick(ROWS, 1) == [(31,), (25,), (40,)], (
        "itemgetter(1) returns the bare item, not a tuple. Wrap it in a one-item tuple: (value,)."
    )


def test_pick_works_on_dicts_and_empty():
    people = [{"name": "ann", "age": 31}, {"name": "bo", "age": 25}]
    assert pick(people, "age", "name") == [(31, "ann"), (25, "bo")], "itemgetter also works with dict keys."
    assert pick([], 0) == [], "No rows, no tuples."


def test_pick_needs_an_index():
    with pytest.raises(ValueError):
        pick(ROWS)


def test_call_method():
    assert call_method(["a,b", "c"], "split", ",") == [["a", "b"], ["c"]], "Pass the extra arguments to the method: methodcaller(name, *args)."
    assert call_method(["  hi ", "yo  "], "strip") == ["hi", "yo"], "With no extra arguments, call the method with none."
    assert call_method([[3, 1], [2]], "count", 3) == [1, 0], "methodcaller works on any object with that method, not only strings."
    assert call_method([], "upper") == [], "No items, empty list."


def test_call_method_returns_list():
    assert isinstance(call_method(["a"], "upper"), list), "Return a list, not a map object: wrap map(...) in list()."


CONFIG = {"db": {"hosts": ["a.local", "b.local"], "port": 5432}, "debug": False}


def test_get_path_found():
    assert get_path(CONFIG, "db", "hosts", 1) == "b.local", "Go into each level in turn: CONFIG['db']['hosts'][1]."
    assert get_path(CONFIG, "db", "port") == 5432
    assert get_path(CONFIG, "debug") is False, "A found value that is False is still found: do not treat falsy values as missing."


def test_get_path_no_keys():
    assert get_path(CONFIG) is CONFIG, "With no keys, reduce returns the start value: the data itself."


def test_get_path_missing():
    assert get_path(CONFIG, "db", "user") is None, "A missing key gives the default (None). Catch KeyError."
    assert get_path(CONFIG, "db", "hosts", 5) is None, "An index out of range gives the default. Catch IndexError."
    assert get_path(CONFIG, "db", "port", 0, default="?") == "?", "An int cannot be indexed: catch TypeError and return default."
    assert get_path(CONFIG, "nope", "deeper", default=0) == 0, "Stop at the first missing step and return default."
