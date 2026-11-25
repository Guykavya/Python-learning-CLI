import numpy as np
import pandas as pd

from solution import conversion_losses


def slow(raw, clean):
    out = {}
    for col in raw.columns:
        if col not in clean.columns:
            continue
        lost, examples = 0, []
        for r, c in zip(raw[col].tolist(), clean[col].tolist()):
            r_empty = r is None or (isinstance(r, float) and np.isnan(r)) or str(r).strip() == ""
            if not r_empty and pd.isna(c):
                lost += 1
                if r not in examples and len(examples) < 3:
                    examples.append(r)
        out[col] = {"lost": lost, "examples": examples}
    return out


def test_the_example():
    raw = pd.DataFrame({"price": ["10", "free", " ", None, "n.a.", "free"], "qty": ["1", "2", "3", "4", "5", "6"]})
    clean = pd.DataFrame({"price": pd.to_numeric(raw["price"], errors="coerce"), "qty": pd.to_numeric(raw["qty"])})
    raw_before, clean_before = raw.copy(), clean.copy()
    got = conversion_losses(raw, clean)
    pd.testing.assert_frame_equal(raw, raw_before, obj="the raw frame")
    pd.testing.assert_frame_equal(clean, clean_before, obj="the clean frame")
    assert isinstance(got, dict), f"return a dict, not a {type(got).__name__}."
    assert list(got) == ["price", "qty"], f"one entry per shared column, in the order of raw; got {list(got)}."
    assert got["price"] == {"lost": 3, "examples": ["free", "n.a."]}, (
        f"price: the blank ' ' and the missing value were empty already, so they are not losses; 'free' (twice) and 'n.a.' are. "
        f"Expected lost 3 and the distinct examples ['free', 'n.a.'], got {got['price']}.")
    assert got["qty"] == {"lost": 0, "examples": []}, f"qty lost nothing, got {got['qty']}."


def test_at_most_three_distinct_examples_in_order_of_appearance():
    raw = pd.DataFrame({"v": ["a", "b", "a", "c", "d", "e", "b", "1"]})
    clean = pd.DataFrame({"v": pd.to_numeric(raw["v"], errors="coerce")})
    got = conversion_losses(raw, clean)["v"]
    assert got["lost"] == 7, f"7 of the 8 values are not numbers; lost should be 7, got {got['lost']}."
    assert got["examples"] == ["a", "b", "c"], f"the first three DISTINCT lost texts in order: ['a', 'b', 'c'], got {got['examples']}."


def test_texts_are_given_as_they_were():
    raw = pd.DataFrame({"v": ["  Rs. ??  ", "5"]})
    clean = pd.DataFrame({"v": [np.nan, 5.0]})
    got = conversion_losses(raw, clean)["v"]
    assert got["examples"] == ["  Rs. ??  "], f"report the raw text unchanged (do not strip it); got {got['examples']}."


def test_only_columns_in_both_frames_and_other_dtypes():
    raw = pd.DataFrame({"when": ["2025-01-01", "31/02/2025", ""], "text": ["x", "y", "z"], "extra": ["1", "2", "3"]})
    clean = pd.DataFrame({"when": pd.to_datetime(["2025-01-01", None, None]), "text": ["x", "y", "z"], "added": [1, 2, 3]})
    got = conversion_losses(raw, clean)
    assert list(got) == ["when", "text"], f"only the columns that exist in both frames, in raw order; got {list(got)}."
    assert got["when"] == {"lost": 1, "examples": ["31/02/2025"]}, f"one impossible date was lost (the empty text was empty already); got {got['when']}."
    assert got["text"]["lost"] == 0, "a text column that was not converted loses nothing."


def test_random_columns_against_the_slow_loop():
    rng = np.random.default_rng(57)
    n = 400
    pool = np.array(["1", "2.5", "x", "n/a?", " ", "", "ten", "9", "Rs 5", "3"], dtype=object)
    raw = pd.DataFrame({f"c{i}": rng.choice(pool, n) for i in range(3)})
    raw.loc[rng.choice(n, 30, replace=False), "c0"] = None
    clean = raw.apply(lambda col: pd.to_numeric(col, errors="coerce"))
    got = conversion_losses(raw, clean)
    assert got == slow(raw, clean), "the counts or examples differ from the slow row-by-row audit."
