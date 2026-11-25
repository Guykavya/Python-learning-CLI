import pandas as pd

from solution import split_product_code


def listed(series):
    return [None if pd.isna(v) else v for v in series.tolist()]


def ints(series):
    return [None if pd.isna(v) else int(v) for v in series.tolist()]


def test_columns_and_dtypes():
    out = split_product_code(pd.Series(["EL-2024-0042"]))
    assert list(out.columns) == ["category", "year", "number"], (
        "use named groups (?P<category>...), (?P<year>...), (?P<number>...). Got columns %s." % list(out.columns))
    assert str(out["year"].dtype) == "Int64" and str(out["number"].dtype) == "Int64", (
        "year and number must be the nullable integer type Int64. Got %s and %s." % (out["year"].dtype, out["number"].dtype))


def test_good_codes():
    out = split_product_code(pd.Series(["EL-2024-0042", "HM-2023-0007", "FD-2025-1234", "ZZ-1999-0000"]))
    assert out["category"].tolist() == ["EL", "HM", "FD", "ZZ"]
    assert ints(out["year"]) == [2024, 2023, 2025, 1999], "got years %s" % ints(out["year"])
    assert ints(out["number"]) == [42, 7, 1234, 0], "0042 must become the integer 42. Got %s." % ints(out["number"])


def test_spaces_around_are_stripped():
    out = split_product_code(pd.Series(["  EL-2024-0042", "HM-2023-0007  "]))
    assert out["category"].tolist() == ["EL", "HM"] and ints(out["year"]) == [2024, 2023]


def test_non_matching_rows_are_fully_missing():
    bad = ["el-2024-0042", "EL-24-0042", "E-2024-0042", "EL-2024-042", "EL-2024-00421", "EL-2024-0042-X",
           "XEL-2024-0042", "EL 2024 0042", "", "EL-2024-0042\nEL-2024-0043"]
    out = split_product_code(pd.Series(bad))
    assert out.isna().all(axis=1).tolist() == [True] * len(bad), (
        "every one of these must give a row of three missing values (anchor the pattern, match the WHOLE text). "
        "Rows that matched: %s." % [b for b, flag in zip(bad, out.isna().all(axis=1)) if not flag])


def test_missing_input_gives_missing_row():
    out = split_product_code(pd.Series(["EL-2024-0042", None, float("nan")]))
    assert out.isna().all(axis=1).tolist() == [False, True, True], "got %s" % out.isna().all(axis=1).tolist()


def test_no_half_filled_rows():
    out = split_product_code(pd.Series(["EL-2024-0042", "EL-2024-xx42", "EL-20x4-0042"]))
    assert out.isna().sum(axis=1).tolist() == [0, 3, 3], "a row is either complete or completely missing. Got %s." % out.isna().sum(axis=1).tolist()


def test_index_kept_and_input_unchanged():
    s = pd.Series(["EL-2024-0042", "nope"], index=[3, 9])
    out = split_product_code(s)
    assert out.index.tolist() == [3, 9], "keep the index of the input."
    assert s.tolist() == ["EL-2024-0042", "nope"]


def test_counting_bad_codes_works_on_the_result():
    s = pd.Series(["EL-2024-0042", "bad", "HM-2023-0007", None])
    assert int(split_product_code(s).isna().any(axis=1).sum()) == 2
