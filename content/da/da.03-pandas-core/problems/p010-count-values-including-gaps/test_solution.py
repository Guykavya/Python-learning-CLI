from collections import Counter

import pandas as pd

from solution import category_counts


def expected(values):
    counter = Counter("(missing)" if v is None else v for v in values)
    rows = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
    return [k for k, _ in rows], [c for _, c in rows], [c / len(values) for _, c in rows]


def check(values):
    s = pd.Series(values, dtype="str")
    out = category_counts(s)
    labels, counts, shares = expected(values)
    assert out.columns.tolist() == ["label", "count", "share"], "columns must be label, count, share; got %s." % out.columns.tolist()
    assert out["label"].tolist() == labels, "label order is wrong: count descending, then label A-Z. Got %s, expected %s." % (out["label"].tolist(), labels)
    assert out["count"].tolist() == counts, "counts differ: got %s, expected %s." % (out["count"].tolist(), counts)
    for got, want in zip(out["share"].tolist(), shares):
        assert abs(got - want) < 1e-12, "share = count / len(s) with the missing values INCLUDED in len(s): got %s, expected %s." % (got, want)
    assert out.index.tolist() == list(range(len(labels))), "index must be 0, 1, 2, ... (reset_index(drop=True))."


def test_example():
    check(["Pune", "Agra", None, "Pune", "Delhi", "Agra", "Pune", None])


def test_ties_sorted_alphabetically():
    check(["b", "a", "c", "a", "b", "c", "d"])


def test_missing_is_the_largest_group():
    check([None, None, None, "x", "y"])


def test_no_missing_values_no_missing_row():
    out = category_counts(pd.Series(["x", "y", "x"]))
    assert "(missing)" not in out["label"].tolist(), "no gaps in the data: do not invent a (missing) row."
    assert out["count"].tolist() == [2, 1]


def test_all_missing():
    check([None, None])


def test_input_not_changed():
    s = pd.Series(["a", None, "a"])
    before = s.copy()
    category_counts(s)
    pd.testing.assert_series_equal(s, before, obj="the input Series")
