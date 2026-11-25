import math
from collections import Counter

import numpy as np
import pandas as pd

from solution import profile

COLS = ["dtype", "missing", "unique", "top", "min", "max"]


def make():
    return pd.DataFrame({
        "city": ["Pune", "Agra", "Pune", None, "Agra", "Delhi", "Pune", "Surat"],
        "qty": [1, 2, 2, 2, None, 5, 5, 1],
        "price": [10.5, 3.25, 3.25, 7.0, 7.0, 7.0, None, 1.0],
        "paid": [True, False, True, True, True, False, True, True],
        "when": pd.to_datetime(["2025-01-02", "2025-01-02", "2025-01-03", None, "2025-01-03", "2025-01-05", "2025-01-02", "2025-01-09"]),
        "empty": [None] * 8,
        "id": range(8),
    })


def expected_top(s, top):
    counts = Counter(v for v in s.tolist() if not pd.isna(v))
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:top]


def test_shape_index_and_columns():
    df = make()
    before = df.copy()
    p = profile(df)
    pd.testing.assert_frame_equal(df, before, obj="the input frame")
    assert isinstance(p, pd.DataFrame), f"return a DataFrame, not a {type(p).__name__}."
    assert p.index.tolist() == df.columns.tolist(), f"one row per column, in the original order; the index should be {df.columns.tolist()}, got {p.index.tolist()}."
    assert p.columns.tolist() == COLS, f"columns should be {COLS}, got {p.columns.tolist()}."


def test_dtype_missing_unique_column_by_column():
    df = make()
    p = profile(df)
    for c in df.columns:
        s = df[c]
        assert p.loc[c, "dtype"] == str(s.dtype), f"{c}: dtype should be {str(s.dtype)!r}, got {p.loc[c, 'dtype']!r}."
        assert p.loc[c, "missing"] == int(s.isna().sum()), f"{c}: missing should be {int(s.isna().sum())}, got {p.loc[c, 'missing']!r}."
        assert p.loc[c, "unique"] == s.dropna().nunique(), f"{c}: unique counts distinct NON-missing values: {s.dropna().nunique()}, got {p.loc[c, 'unique']!r}."


def test_top_values_with_counts_and_tie_order():
    df = make()
    for top in (1, 3, 10):
        p = profile(df, top=top)
        for c in df.columns:
            want = expected_top(df[c], top)
            got = p.loc[c, "top"]
            assert isinstance(got, list), f"{c}: top must be a list of (value, count) pairs, got {type(got).__name__}."
            assert [(v, n) for v, n in got] == want, (
                f"{c} (top={top}): expected {want}, got {got}. Most frequent first; equal counts: smaller value first; missing values are not counted.")
    p = profile(df, top=2)
    assert p.loc["city", "top"] == [("Pune", 3), ("Agra", 2)], f"city: Pune appears 3 times, Agra 2; got {p.loc['city', 'top']}."
    assert p.loc["qty", "top"] == [(2.0, 3), (1.0, 2)], f"qty: 2 appears 3 times, then 1 and 5 tie with 2: the smaller value (1) comes first; got {p.loc['qty', 'top']}."
    assert p.loc["empty", "top"] == [], f"a column with no values has an empty list, got {p.loc['empty', 'top']}."


def test_min_max_only_for_numbers():
    df = make()
    p = profile(df)
    assert (p.loc["qty", "min"], p.loc["qty", "max"]) == (1.0, 5.0), f"qty min and max are 1.0 and 5.0, got {p.loc['qty', 'min']} and {p.loc['qty', 'max']}."
    assert (p.loc["price", "min"], p.loc["price", "max"]) == (1.0, 10.5), "price min and max are 1.0 and 10.5."
    assert (p.loc["id", "min"], p.loc["id", "max"]) == (0.0, 7.0), "an integer column gets min and max too, as floats."
    for c in ["city", "paid", "when", "empty"]:
        assert math.isnan(p.loc[c, "min"]) and math.isnan(p.loc[c, "max"]), (
            f"{c}: min and max are NaN for text, booleans, dates and columns without values (a boolean is not a number here); got {p.loc[c, 'min']!r}, {p.loc[c, 'max']!r}.")


def test_random_table_matches_direct_calls():
    rng = np.random.default_rng(55)
    n = 300
    df = pd.DataFrame({
        "a": rng.integers(0, 6, n),
        "b": np.where(rng.random(n) < 0.1, np.nan, rng.integers(0, 4, n)),
        "c": rng.choice(["x", "y", "z", None], n),
    })
    p = profile(df, top=3)
    for c in df.columns:
        want = expected_top(df[c], 3)
        assert [(v, k) for v, k in p.loc[c, "top"]] == want, f"{c}: top values differ from a Counter-based count: expected {want}, got {p.loc[c, 'top']}."
        assert p.loc[c, "missing"] == df[c].isna().sum() and p.loc[c, "unique"] == df[c].nunique(), f"{c}: missing or unique differ from the direct pandas calls."
