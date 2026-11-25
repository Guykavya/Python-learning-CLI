import pandas as pd

from solution import replace_sentinels


def sample():
    return pd.DataFrame({
        "age": [25, -1, 999, 40, 999],
        "income": [0, 52000, 38000, 0, 41000],
        "city": ["Pune", "Delhi", "Pune", "Delhi", "Pune"],
        "score": [0, 5, 0, 7, 8],
    })


def listed(series):
    return [None if pd.isna(v) else float(v) for v in series.tolist()]


def test_codes_become_missing_in_their_own_column():
    out, _ = replace_sentinels(sample(), {"age": [-1, 999], "income": [0]})
    assert listed(out["age"]) == [25.0, None, None, 40.0, None], "age codes -1 and 999 must become NaN. Got %s." % listed(out["age"])
    assert listed(out["income"]) == [None, 52000.0, 38000.0, None, 41000.0], "income code 0 must become NaN."


def test_other_columns_are_untouched():
    out, _ = replace_sentinels(sample(), {"age": [-1, 999], "income": [0]})
    assert out["city"].tolist() == sample()["city"].tolist(), "city is not in codes: leave it alone."
    assert out["score"].tolist() == [0, 5, 0, 7, 8], (
        "0 is a code for income only. In score it is a real value and must stay. Codes belong to a column.")


def test_counts_per_column_in_the_order_of_codes():
    _, counts = replace_sentinels(sample(), {"age": [-1, 999], "income": [0]})
    assert counts == {"age": 3, "income": 2}, "counts = how many cells were codes, per column. Got %s." % counts
    assert list(counts) == ["age", "income"], "keep the order of `codes`."


def test_column_without_codes_counts_zero():
    _, counts = replace_sentinels(sample(), {"age": [12345], "score": [99, 98]})
    assert counts == {"age": 0, "score": 0}, "a column listed in codes always has a key, with 0 when nothing matched. Got %s." % counts


def test_already_missing_values_are_not_counted():
    df = pd.DataFrame({"age": [999, None, 30.0, None, 999]})
    out, counts = replace_sentinels(df, {"age": [999]})
    assert counts == {"age": 2}, "only the 999s count, not the values that were already missing. Got %s." % counts
    assert out["age"].isna().sum() == 4


def test_input_frame_is_not_changed():
    df = sample()
    replace_sentinels(df, {"age": [-1, 999], "income": [0]})
    pd.testing.assert_frame_equal(df, sample(), obj="the input frame (do not edit the raw data, work on a copy)")


def test_mean_is_repaired():
    df = sample()
    out, _ = replace_sentinels(df, {"age": [-1, 999]})
    assert round(df["age"].mean(), 1) == 412.4
    assert round(out["age"].mean(), 1) == 32.5, "after the replacement the mean of age is (25+40)/2 = 32.5. Got %s." % out["age"].mean()


def test_empty_codes_changes_nothing():
    out, counts = replace_sentinels(sample(), {})
    assert counts == {}, "no codes, no counts."
    pd.testing.assert_frame_equal(out, sample())
