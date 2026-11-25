import math

import pandas as pd

from solution import cap_discounts


def frame():
    return pd.DataFrame({
        "item": ["a", "b", "c", "d", "e", "f"],
        "discount": [5.0, 30.0, None, 20.0, 20.5, 0.0],
        "price": [100, 200, 300, 400, 500, 600],
    }, index=[3, 4, 5, 6, 7, 8])


def slow(values, cap):
    out = []
    for v in values:
        if isinstance(v, float) and math.isnan(v):
            out.append(v)
        else:
            out.append(cap if v > cap else v)
    return out


def test_example():
    df = pd.DataFrame({"item": ["a", "b", "c", "d"], "discount": [5.0, 30.0, None, 20.0]})
    got = cap_discounts(df, 20)["discount"].tolist()
    assert got[0] == 5.0 and got[1] == 20.0 and math.isnan(got[2]) and got[3] == 20.0, "expected [5.0, 20.0, nan, 20.0]; got %s." % got


def test_shape_and_labels_are_kept():
    df = frame()
    out = cap_discounts(df, 20)
    assert out.shape == df.shape, "the table must keep every row: shape %s, expected %s. A filter drops rows; where/mask keep them." % (out.shape, df.shape)
    assert out.index.tolist() == df.index.tolist() and out.columns.tolist() == df.columns.tolist()


def test_values_match_a_loop():
    df = frame()
    for cap in (0, 5, 20, 20.5, 100):
        got = cap_discounts(df, cap)["discount"].tolist()
        want = slow(df["discount"].tolist(), cap)
        assert len(got) == len(want)
        for g, w in zip(got, want):
            assert (math.isnan(g) and math.isnan(w)) or g == w, "cap=%s: got %s, expected %s (above the cap -> cap; missing stays missing)." % (cap, got, want)


def test_other_columns_untouched():
    df = frame()
    out = cap_discounts(df, 20)
    assert out["price"].tolist() == df["price"].tolist() and out["item"].tolist() == df["item"].tolist()
    assert str(out["discount"].dtype) == "float64"


def test_input_not_changed():
    df = frame()
    before = df.copy()
    cap_discounts(df, 10)
    pd.testing.assert_frame_equal(df, before, obj="the input frame (discount must be changed in the returned copy only)")
