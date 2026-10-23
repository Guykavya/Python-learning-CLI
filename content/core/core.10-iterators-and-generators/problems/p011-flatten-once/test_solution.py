from solution import flatten_once


def test_basic():
    assert flatten_once([[1, 2], [3], [], [4, 5]]) == [1, 2, 3, 4, 5], "Glue the inner lists together in order; empty inner lists add nothing."


def test_strings_and_tuples():
    assert flatten_once(["ab", "cd"]) == ["a", "b", "c", "d"], "Strings are iterables of characters."
    assert flatten_once(((1,), (2, 3))) == [1, 2, 3], "Tuples work too."


def test_only_one_level():
    assert flatten_once([[1, [2]], [3]]) == [1, [2], 3], "Flatten only ONE level: the inner list [2] stays a list."


def test_empty_and_generator_input():
    assert flatten_once([]) == [], "No lists, no items."
    assert flatten_once([n] * n for n in range(3)) == [1, 2, 2], "The outer iterable may be a generator."


def test_returns_list():
    assert isinstance(flatten_once([[1]]), list), "Return a real list, not a chain object."
