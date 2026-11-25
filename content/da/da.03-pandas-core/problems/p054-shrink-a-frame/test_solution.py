import numpy as np
import pandas as pd

from solution import shrink


def make(n=20_000, seed=54):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "order_id": np.arange(100_000, 100_000 + n),
        "qty": rng.integers(1, 8, n),
        "stars": rng.integers(-3, 4, n),
        "price_quarter": rng.integers(40, 400, n) / 4,
        "price_exact": rng.gamma(4.0, 120.0, n).round(2),
        "city": rng.choice(["Pune", "Delhi", "Agra", "Jaipur", "Surat"], n),
        "ref_code": [f"R{i}" for i in range(n)],
        "paid": rng.random(n) < 0.9,
        "when": pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 120, n), unit="D"),
    })


def mem(df):
    return int(df.memory_usage(deep=True).sum())


def test_dtypes_of_each_kind_of_column():
    df = make(2000)
    got = shrink(df)
    dtypes = {c: str(t) for c, t in got.dtypes.items()}
    assert dtypes["qty"] == "int8", f"qty holds 1..7, so int8; got {dtypes['qty']}. Use pd.to_numeric(s, downcast='integer')."
    assert dtypes["stars"] == "int8", f"stars holds -3..3, so a signed int8; got {dtypes['stars']}."
    assert dtypes["order_id"] == "int32", f"order_id goes up to about 102,000: int32; got {dtypes['order_id']}."
    assert dtypes["price_quarter"] == "float32", f"multiples of 0.25 are exact in float32, so price_quarter can shrink; got {dtypes['price_quarter']}."
    assert dtypes["price_exact"] == "float64", (
        f"prices such as 315.76 change when stored as float32; a shrink must not change values, so price_exact stays float64; got {dtypes['price_exact']}.")
    assert dtypes["city"] == "category", f"city has 5 distinct values: category; got {dtypes['city']}."
    assert dtypes["ref_code"] != "category", "ref_code has one distinct value per row (2000 > 50): it must not become a category."
    assert dtypes["paid"] == "bool", f"booleans stay as they are, got {dtypes['paid']}."
    assert dtypes["when"] == str(df["when"].dtype), f"dates stay as they are, got {dtypes['when']}."


def test_every_value_is_equal_and_input_is_unchanged():
    df = make(3000)
    before = df.copy()
    got = shrink(df)
    pd.testing.assert_frame_equal(df, before, obj="the input frame")
    assert got.columns.tolist() == df.columns.tolist(), "keep the column order."
    assert got.index.equals(df.index), "keep the index."
    for c in df.columns:
        pd.testing.assert_series_equal(got[c].astype(df[c].dtype), df[c], obj=f"column {c!r} after shrink")


def test_memory_is_at_most_half():
    df = make().drop(columns=["ref_code", "price_exact"])   # an id text column and random decimals cannot shrink
    got = shrink(df)
    assert mem(got) <= 0.5 * mem(df), f"memory went from {mem(df):,} to {mem(got):,} bytes; it must be at most half. Shrink every integer, exact-float and low-cardinality text column."


def test_missing_values_survive():
    df = pd.DataFrame({"f": [0.5, np.nan, 2.0], "g": [0.1, np.nan, 2.0], "t": ["a", None, "a"], "i": [1, 2, 3]})
    got = shrink(df)
    assert str(got["f"].dtype) == "float32" and got["f"].isna().tolist() == [False, True, False], (
        f"NaN is allowed in float32 and must stay missing: expected float32 with the gap in row 1, got {got['f'].dtype}.")
    assert str(got["g"].dtype) == "float64", "0.1 is not exact in float32, so g stays float64."
    assert got["t"].isna().tolist() == [False, True, False] and str(got["t"].dtype) == "category", f"text with a gap becomes a category and keeps the gap; got {got['t'].dtype}."
    assert str(got["i"].dtype) == "int8", f"got {got['i'].dtype}."


def test_a_text_column_with_many_distinct_values_stays_text():
    df = pd.DataFrame({"code": [f"c{i}" for i in range(60)] * 2, "few": ["x", "y"] * 60})
    got = shrink(df)
    assert str(got["code"].dtype) != "category", "60 distinct values is more than 50: the column must stay text."
    assert str(got["few"].dtype) == "category", "2 distinct values: category."
