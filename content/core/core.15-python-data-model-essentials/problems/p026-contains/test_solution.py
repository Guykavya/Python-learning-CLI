from solution import Interval, WordSet


def test_interval_inside_and_outside():
    iv = Interval(1, 10)
    assert 5 in iv, "5 is between 1 and 10, so `5 in Interval(1, 10)` should be True."
    assert 0 not in iv and 11 not in iv, "Values outside the range are not in the interval."


def test_interval_ends_included():
    iv = Interval(1, 10)
    assert 1 in iv and 10 in iv, "Both ends are included: lo <= x <= hi."


def test_interval_floats_and_negatives():
    assert 2.5 in Interval(2, 3), "Floats can be inside the interval too."
    assert 10.5 not in Interval(1, 10), "10.5 is above 10."
    assert -3 in Interval(-5, -1), "Negative ranges work as well."


def test_interval_non_numbers_are_false():
    iv = Interval(1, 10)
    assert "a" not in iv, "A string is not in a numeric interval: answer False, do not raise TypeError."
    assert None not in iv, "None is not in the interval either."


def test_interval_is_not_iterable():
    iv = Interval(1, 10)
    assert not hasattr(iv, "__iter__"), "Interval must answer `in` through __contains__, without storing or iterating values."


def test_wordset_ignores_case():
    ws = WordSet(["Hello", "World"])
    assert "hello" in ws and "WORLD" in ws and "Hello" in ws, "Membership must ignore case."
    assert "hell" not in ws and "x" not in ws, "Only whole words match."


def test_wordset_non_strings_false():
    ws = WordSet(["Hello"])
    assert 3 not in ws and None not in ws, "Non-strings are simply not in the set (False, no AttributeError)."


def test_wordset_casefold():
    assert "STRASSE" in WordSet(["stra\u00dfe"]), "Use casefold(), not lower(): 'ß' folds to 'ss'."


def test_wordset_empty():
    assert "a" not in WordSet([]), "An empty WordSet contains nothing."
