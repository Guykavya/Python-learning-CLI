from solution import merge_counts


def test_example():
    assert merge_counts({"tea": 3, "milk": 1}, {"milk": 2, "bread": 5}) == {"tea": 3, "milk": 3, "bread": 5}


def test_order_first_seen():
    r = merge_counts({"b": 1}, {"a": 1, "b": 1})
    assert list(r) == ["b", "a"], "Keys keep the order in which they were first seen."


def test_zero_dropped():
    assert merge_counts({"tea": 2}, {"tea": -2, "jam": 1}) == {"jam": 1}, "A total of 0 is left out."


def test_none_given():
    assert merge_counts() == {}, "With no dicts, return an empty dict (do not read counts[0])."


def test_one_dict_is_copied():
    d = {"x": 1}
    r = merge_counts(d)
    assert r == {"x": 1}
    assert r is not d, "Return a NEW dict, even for one input."


def test_inputs_unchanged():
    a = {"tea": 3, "milk": 1}
    b = {"milk": 2}
    merge_counts(a, b)
    merge_counts(a, b)
    assert a == {"tea": 3, "milk": 1} and b == {"milk": 2}, (
        "An input dict changed. Did you start with totals = counts[0]? That is an alias, not a copy.")


def test_many():
    dicts = [{"n": 1} for _ in range(100)]
    assert merge_counts(*dicts) == {"n": 100}
