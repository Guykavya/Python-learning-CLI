import numpy as np
import pandas as pd

from solution import validate_table


def frame():
    return pd.DataFrame({"id": [1, 2, 2, 4, 5], "age": [25, 17, 130, np.nan, 40],
                         "city": ["Pune", "Delhi", "Goa", "Pune", "Pune"]}, index=[100, 101, 102, 103, 104])


RULES = {
    "id is unique": lambda d: ~d["id"].duplicated(keep=False),
    "age in 18..75": lambda d: d["age"].between(18, 75) | d["age"].isna(),
    "city is known": lambda d: d["city"].isin(["Pune", "Delhi"]),
}


def test_worked_example():
    out = validate_table(frame(), RULES)
    assert out == [("id is unique", 2, [101, 102]), ("age in 18..75", 2, [101, 102]), ("city is known", 1, [102])], (
        "each failing rule gives (name, number of failing rows, first labels); got %s." % (out,))


def test_labels_not_positions():
    out = validate_table(frame(), {"city is known": RULES["city is known"]})
    assert out == [("city is known", 1, [102])], "report the index LABEL (102), not the position (2)."


def test_passing_table_gives_empty_list():
    ok = pd.DataFrame({"id": [1, 2], "age": [30, 40], "city": ["Pune", "Delhi"]})
    assert validate_table(ok, RULES) == [], "a table that passes every rule gives an empty list."


def test_passing_rules_are_not_listed_and_order_is_kept():
    d = frame()
    rules = {"first": RULES["city is known"], "never fails": lambda x: x["id"] > 0, "last": RULES["id is unique"]}
    out = validate_table(d, rules)
    assert [r[0] for r in out] == ["first", "last"], "list only failing rules, in the order of the rules dict. Got %s." % [r[0] for r in out]


def test_at_most_three_ids():
    d = pd.DataFrame({"x": [-1, -2, -3, -4, -5, 6]}, index=list("abcdef"))
    out = validate_table(d, {"x is positive": lambda t: t["x"] > 0})
    assert out == [("x is positive", 5, ["a", "b", "c"])], "n_failed counts all five rows, first_ids shows only the first three labels."


def test_missing_answer_counts_as_fine():
    d = pd.DataFrame({"v": [1.0, np.nan, 3.0]})
    out = validate_table(d, {"v below 2": lambda t: t["v"].lt(2).where(t["v"].notna())})
    assert out == [("v below 2", 1, [2])], "a missing answer from a rule (NaN) means fine; only the row with 3.0 fails."


def test_types_and_input_not_changed():
    d = frame()
    before = d.copy()
    out = validate_table(d, RULES)
    pd.testing.assert_frame_equal(d, before, obj="the input frame")
    assert type(out[0][1]) is int and isinstance(out[0][2], list), "n_failed is a plain int and first_ids a list."
