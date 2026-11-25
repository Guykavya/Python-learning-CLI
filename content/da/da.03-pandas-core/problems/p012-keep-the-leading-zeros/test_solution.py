import pandas as pd

from solution import read_with_codes


def write(tmp_path, text):
    path = tmp_path / "codes.csv"
    path.write_text(text, encoding="utf-8", newline="")
    return path


def test_example(tmp_path):
    df = read_with_codes(write(tmp_path, "pin,product_code,qty\n007,00A1,3\n012,0042,5\n"))
    assert df["pin"].tolist() == ["007", "012"], "pin lost its leading zeros: read it with dtype={'pin': 'str', ...}. Got %s." % df["pin"].tolist()
    assert df["product_code"].tolist() == ["00A1", "0042"], (
        "product_code must stay text: '0042' must not become 42. Got %s." % df["product_code"].tolist())


def test_dtypes(tmp_path):
    df = read_with_codes(write(tmp_path, "pin,product_code,qty\n110,9,1\n560,10,2\n"))
    assert str(df["pin"].dtype) == "str", "pin dtype is %s; identifiers are text even when every character is a digit." % df["pin"].dtype
    assert str(df["product_code"].dtype) == "str", "product_code dtype is %s, expected str." % df["product_code"].dtype
    assert str(df["qty"].dtype) == "int64", "qty must still be numeric (int64), not text: only the two codes get a dtype. Got %s." % df["qty"].dtype
    assert df["pin"].tolist() == ["110", "560"]


def test_long_digit_codes_keep_every_digit(tmp_path):
    df = read_with_codes(write(tmp_path, "pin,product_code,qty\n000123,12345678901234567890,1\n"))
    assert df["product_code"].tolist() == ["12345678901234567890"], "a long code must not lose digits (it would not fit an int64)."
    assert df["pin"].tolist() == ["000123"]


def test_missing_code_stays_missing(tmp_path):
    df = read_with_codes(write(tmp_path, "pin,product_code,qty\n007,,3\n,0042,4\n"))
    assert df["product_code"].isna().tolist() == [True, False], "an empty field is a missing code, not the text 'nan'."
    assert df["pin"].isna().tolist() == [False, True]
    assert df["product_code"].dropna().tolist() == ["0042"]
