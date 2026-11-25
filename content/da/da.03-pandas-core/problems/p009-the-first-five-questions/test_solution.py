import pandas as pd

from solution import first_look


def frame():
    return pd.DataFrame({
        "id": [1, 2, 3, 3, 5, 1],
        "name": ["a", None, "c", "c", "e", "a"],
        "price": [1.5, 2.5, None, None, 5.5, 1.5],
        "when": pd.to_datetime(["2024-01-01", "2024-01-02", None, None, "2024-01-05", "2024-01-01"]),
    })


def test_example():
    df = pd.DataFrame({"a": [1, 2, 2], "b": ["x", None, None]})
    out = first_look(df)
    assert out["rows"] == 3 and out["cols"] == 2, "rows and cols come from df.shape."
    assert out["missing"] == {"a": 0, "b": 2}, "missing per column: df.isna().sum(), got %s." % out["missing"]
    assert out["duplicate_rows"] == 1, "row 2 repeats row 1 once; got %s." % out["duplicate_rows"]


def test_keys_and_counts():
    out = first_look(frame())
    assert set(out) == {"rows", "cols", "dtypes", "missing", "duplicate_rows"}, "the dict needs exactly the five keys, got %s." % sorted(out)
    assert out["rows"] == 6 and out["cols"] == 4


def test_dtypes_are_strings_for_every_column():
    df = frame()
    out = first_look(df)
    want = {c: str(t) for c, t in df.dtypes.items()}
    assert out["dtypes"] == want, "dtypes must map each column to str(dtype); got %s, expected %s." % (out["dtypes"], want)
    assert all(type(v) is str for v in out["dtypes"].values()), "use str(dtype): the dtype objects are not plain strings."


def test_missing_counts_and_types():
    out = first_look(frame())
    assert out["missing"] == {"id": 0, "name": 1, "price": 2, "when": 2}, "wrong missing counts: %s." % out["missing"]
    assert all(type(v) is int for v in out["missing"].values()), "counts must be plain ints (int(...))."


def test_duplicates_count_repeats_after_the_first():
    df = frame()
    out = first_look(df)
    assert out["duplicate_rows"] == 2, "rows 3 and 5 repeat earlier rows (3 and 0): expected 2, got %s. Missing values count as equal." % out["duplicate_rows"]
    assert type(out["duplicate_rows"]) is int


def test_no_missing_no_duplicates():
    df = pd.DataFrame({"x": [1, 2], "y": [3.0, 4.0]})
    out = first_look(df)
    assert out["missing"] == {"x": 0, "y": 0} and out["duplicate_rows"] == 0


def test_input_not_changed():
    df = frame()
    before = df.copy()
    first_look(df)
    pd.testing.assert_frame_equal(df, before, obj="the input frame")
