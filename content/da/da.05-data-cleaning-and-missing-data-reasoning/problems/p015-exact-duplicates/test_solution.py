import pandas as pd

from solution import drop_exact_duplicates


def sample():
    return pd.DataFrame({
        "id": [1, 2, 2, 3, 3, 4, 4],
        "city": ["Pune", "Delhi", "Delhi", "Pune", "pune", None, None],
        "age": [25, 30, 30, 41, 41, None, None],
    })


def test_first_copy_is_kept_with_original_labels():
    clean, n = drop_exact_duplicates(sample())
    assert clean.index.tolist() == [0, 1, 3, 4, 5], (
        "keep the first copy of each row and the original index labels. Got labels %s." % clean.index.tolist())
    assert n == 2, "2 rows were removed (labels 2 and 6). Got %r." % n


def test_case_difference_is_not_an_exact_duplicate():
    clean, _ = drop_exact_duplicates(sample())
    assert clean.loc[4, "city"] == "pune", "row 4 differs from row 3 only by case, but they are NOT exact duplicates."


def test_missing_values_are_equal_for_duplicates():
    df = pd.DataFrame({"a": [None, None, 1.0], "b": ["x", "x", "x"]})
    clean, n = drop_exact_duplicates(df)
    assert n == 1 and clean.index.tolist() == [0, 2], (
        "two rows with a missing value in the same place and equal values elsewhere are duplicates. Got %s, %r."
        % (clean.index.tolist(), n))


def test_count_is_a_plain_int():
    _, n = drop_exact_duplicates(sample())
    assert type(n) is int, "return the count as a plain int, not %s." % type(n).__name__


def test_nothing_to_remove():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    clean, n = drop_exact_duplicates(df)
    assert n == 0 and clean.equals(df), "when there are no repeats, return the same rows and 0."


def test_all_rows_equal():
    df = pd.DataFrame({"a": [5, 5, 5, 5]})
    clean, n = drop_exact_duplicates(df)
    assert clean.index.tolist() == [0] and n == 3, "four identical rows leave one (the first) and remove 3."


def test_values_of_surviving_rows_are_unchanged():
    clean, _ = drop_exact_duplicates(sample())
    assert clean["id"].tolist() == [1, 2, 3, 3, 4]
    assert clean["age"].dropna().tolist() == [25.0, 30.0, 41.0, 41.0]


def test_input_is_not_changed():
    df = sample()
    drop_exact_duplicates(df)
    pd.testing.assert_frame_equal(df, sample(), obj="the input frame")
