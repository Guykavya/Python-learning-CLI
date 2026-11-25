import pandas as pd

from solution import compare_keys


def test_example_sets_and_counts():
    r = compare_keys([101, 102, 103, 103, 105], [102, 103, 104, 106, 107], "ops", "finance")
    assert r["only_a"] == [101, 105], "only in A: 101 and 105 (sorted). Got %s." % r["only_a"]
    assert r["only_b"] == [104, 106, 107], "only in B: 104, 106, 107. Got %s." % r["only_b"]
    assert r["both"] == [102, 103], "in both: 102 and 103. Got %s." % r["both"]
    assert r["counts"] == {"a": 4, "b": 5, "only_a": 2, "only_b": 3, "both": 2}, (
        "counts use DISTINCT keys: A has 4 (103 is repeated), B has 5. Got %s." % r["counts"])


def test_summary_text():
    r = compare_keys([101, 102, 103, 103, 105], [102, 103, 104, 106, 107], "ops", "finance")
    assert r["summary"] == "ops: 4 | finance: 5 | in both: 2 | only ops: 2 | only finance: 3", "summary text differs. Got %r." % r["summary"]
    r2 = compare_keys([1], [1])
    assert r2["summary"] == "A: 1 | B: 1 | in both: 1 | only A: 0 | only B: 0", "default names are A and B. Got %r." % r2["summary"]


def test_net_difference_hides_two_flows():
    a = list(range(1, 11))          # 10 keys
    b = list(range(4, 14))          # 10 keys: same size, different jobs
    r = compare_keys(a, b)
    assert len(a) == len(b) and r["only_a"] == [1, 2, 3] and r["only_b"] == [11, 12, 13], (
        "the two sets have the same size but 3 keys leave and 3 enter: look at the sets, not at the totals.")


def test_empty_inputs_and_disjoint():
    r = compare_keys([], [])
    assert r["only_a"] == [] and r["both"] == [] and r["counts"]["a"] == 0, "two empty inputs give empty lists and zero counts."
    r = compare_keys([1, 2], [3])
    assert r["both"] == [] and r["only_a"] == [1, 2] and r["only_b"] == [3], "disjoint sets have nothing in common."


def test_series_inputs_give_plain_python_keys_and_are_unchanged():
    a = pd.Series([5, 3, 3, 9])
    b = pd.Series([9, 1])
    r = compare_keys(a, b, "a", "b")
    assert r["both"] == [9] and r["only_a"] == [3, 5] and r["only_b"] == [1], "Series inputs must work. Got %s." % r
    assert all(type(k) is int for k in r["only_a"] + r["only_b"] + r["both"]), "return plain Python ints, not numpy integers."
    assert a.tolist() == [5, 3, 3, 9], "do not sort or change the inputs."
