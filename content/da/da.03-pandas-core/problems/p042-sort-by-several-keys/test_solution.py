import numpy as np
import pandas as pd

from solution import rank_sellers


def python_order(df):
    rows = list(df.itertuples())
    rows.sort(key=lambda r: (pd.isna(r.revenue), 0 if pd.isna(r.revenue) else -r.revenue, r.seller))
    return [r.Index for r in rows]


def test_the_example():
    df = pd.DataFrame({
        "seller": ["Dev", "Asha", "Chitra", "Ben", "Esha"],
        "revenue": [500.0, 500.0, None, 900.0, 500.0],
        "note": list("abcde"),
    })
    before = df.copy()
    out = rank_sellers(df)
    pd.testing.assert_frame_equal(df, before, obj="the input frame")
    assert out["seller"].tolist() == ["Ben", "Asha", "Dev", "Esha", "Chitra"], (
        f"expected ['Ben', 'Asha', 'Dev', 'Esha', 'Chitra'], got {out['seller'].tolist()}. "
        "Revenue descending, then seller ascending; the missing revenue goes last.")
    assert out.index.tolist() == [3, 1, 0, 4, 2], f"keep the original labels: expected [3, 1, 0, 4, 2], got {out.index.tolist()}."
    assert out.columns.tolist() == ["seller", "revenue", "note"], "keep all columns."


def test_missing_revenue_goes_last_even_when_sorting_descending():
    df = pd.DataFrame({"seller": ["A", "B", "C"], "revenue": [None, 1.0, None]})
    out = rank_sellers(df)
    assert out["seller"].tolist() == ["B", "A", "C"], (
        f"missing revenue must be last (na_position='last') and ordered by seller among themselves; got {out['seller'].tolist()}.")


def test_ties_keep_the_original_order():
    df = pd.DataFrame({"seller": ["Kim", "Kim", "Kim", "Al"], "revenue": [10.0, 10.0, 10.0, 10.0], "note": [1, 2, 3, 4]})
    out = rank_sellers(df)
    assert out["note"].tolist() == [4, 1, 2, 3], f"Al first, then the three equal Kim rows in their original order; got {out['note'].tolist()}."


def test_odd_index_and_random_tables():
    rng = np.random.default_rng(42)
    names = np.array(["Asha", "Ben", "Chitra", "Dev", "Esha"])
    for trial in range(25):
        n = int(rng.integers(1, 30))
        rev = rng.integers(0, 4, n).astype(float) * 100
        rev[rng.random(n) < 0.2] = np.nan
        df = pd.DataFrame({"seller": rng.choice(names, n), "revenue": rev, "note": range(n)},
                          index=rng.permutation(n) + 1000)
        want = python_order(df)
        got = rank_sellers(df).index.tolist()
        assert got == want, (
            f"trial {trial}: the order of labels differs from the plain-Python sort.\nexpected {want}\ngot      {got}")
