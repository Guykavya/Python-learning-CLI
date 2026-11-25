import pandas as pd

from solution import audit

COLS = ["dtype", "missing", "unique", "top", "suspect_text"]


def sample():
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6],
        "age": [25.0, None, 31.0, 25.0, 40.0, None],
        "city": ["Pune", "Delhi", "Pune", None, "Delhi", "Pune"],
        "income": ["45000", "52000", "N/A", "", "38000", "45000"],
    })


def is_missing(v):
    return v is None or (isinstance(v, float) and v != v) or v is pd.NA


def test_shape_index_and_column_names():
    out = audit(sample())
    assert list(out.columns) == COLS, "columns must be %s in this order. Got %s." % (COLS, list(out.columns))
    assert list(out.index) == ["id", "age", "city", "income"], (
        "one row per column of the input, the index holds the column names in the original order.")


def test_dtype_matches_pandas():
    df = sample()
    out = audit(df)
    for c in df.columns:
        assert out.loc[c, "dtype"] == str(df[c].dtype), (
            "dtype of %r must be str(df[%r].dtype) = %r, got %r." % (c, c, str(df[c].dtype), out.loc[c, "dtype"]))


def test_missing_counts_match_isna():
    df = sample()
    out = audit(df)
    assert out["missing"].tolist() == [int(df[c].isna().sum()) for c in df.columns] == [0, 2, 1, 0], (
        "missing = df[col].isna().sum(); the empty text in income is NOT missing for pandas. Got %s."
        % out["missing"].tolist())


def test_unique_ignores_missing_values():
    out = audit(sample())
    assert out["unique"].tolist() == [6, 3, 2, 5], (
        "unique counts distinct NON-missing values: age has 25, 31, 40 (not 4). Got %s." % out["unique"].tolist())


def test_top_value_and_ties():
    out = audit(sample())
    assert out.loc["age", "top"] == 25.0, "the most common age is 25.0 (twice). Got %r." % out.loc["age", "top"]
    assert out.loc["city", "top"] == "Pune", "Pune appears 3 times. Got %r." % out.loc["city", "top"]
    assert out.loc["income", "top"] == "45000", "45000 appears twice. Got %r." % out.loc["income", "top"]
    assert out.loc["id", "top"] == 1, "all ids appear once: a tie, so the smallest value wins (1). Got %r." % out.loc["id", "top"]


def test_tie_between_text_values_takes_the_smallest():
    df = pd.DataFrame({"c": ["b", "a", "b", "a", "z"]})
    assert audit(df).loc["c", "top"] == "a", "'a' and 'b' both appear twice: the smaller one, 'a', is the top."


def test_all_missing_column():
    df = pd.DataFrame({"x": [None, None, None], "y": [1, 2, 3]})
    out = audit(df)
    assert is_missing(out.loc["x", "top"]), "a column with nothing in it has top None. Got %r." % out.loc["x", "top"]
    assert out.loc["x", "missing"] == 3 and out.loc["x", "unique"] == 0 and out.loc["x", "suspect_text"] == 0


def test_suspect_text_in_a_number_like_column():
    out = audit(sample())
    assert out.loc["income", "suspect_text"] == 2, (
        "income has 6 values: 4 numbers, 'N/A' and ''. More than half are numbers, so the 2 others are suspects. Got %r."
        % out.loc["income", "suspect_text"])


def test_other_columns_have_zero_suspects():
    out = audit(sample())
    assert out.loc["city", "suspect_text"] == 0, "city is not number-like (no value parses), so suspect_text is 0."
    assert out.loc["id", "suspect_text"] == 0 and out.loc["age", "suspect_text"] == 0, (
        "numeric columns are not text columns: 0.")


def test_spaces_are_stripped_and_missing_text_is_skipped():
    df = pd.DataFrame({"v": [" 12 ", "7", None, "x", "8.5", "9"]})
    out = audit(df)
    assert out.loc["v", "suspect_text"] == 1, (
        "strip first (' 12 ' is a number), skip the missing value, count only 'x'. Got %r." % out.loc["v", "suspect_text"])
    assert out.loc["v", "missing"] == 1 and out.loc["v", "unique"] == 5


def test_exactly_half_numbers_is_not_number_like():
    df = pd.DataFrame({"v": ["1", "2", "a", "b"]})
    assert audit(df).loc["v", "suspect_text"] == 0, (
        "'more than half' means strictly more: 2 of 4 is not enough, so the column is plain text and gets 0.")


def test_input_is_not_changed():
    df = sample()
    audit(df)
    pd.testing.assert_frame_equal(df, sample())
