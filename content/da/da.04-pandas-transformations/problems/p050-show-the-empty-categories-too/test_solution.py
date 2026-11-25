import pandas as pd

from solution import orders_per_size

SIZES = pd.CategoricalDtype(["S", "M", "L", "XL"], ordered=True)


def lines():
    return pd.DataFrame({
        "order_id": [10001, 10001, 10002, 10003, 10004, 10005, 10006, 10007],
        "product_id": ["P1", "P2", "P1", "P3", "P2", "P1", "P4", "P3"],
        "size": pd.Series(["M", "S", "M", "XL", None, "M", "S", "M"], dtype=SIZES),
    })


def test_columns():
    out = orders_per_size(lines())
    assert list(out.columns) == ["size", "orders"], "columns size and orders; got %s" % list(out.columns)
    assert out.index.tolist() == list(range(len(out))), "fresh index"


def test_every_size_listed_in_order():
    out = orders_per_size(lines())
    got = out["size"].astype(str).tolist()
    assert "L" in got, "nobody ordered L, but the report must still list it with 0 (observed=False); got %s" % got
    assert got == ["S", "M", "L", "XL"], "one row per size in the category order S, M, L, XL; got %s" % got


def test_counts():
    out = orders_per_size(lines())
    assert out["orders"].tolist() == [2, 4, 0, 1], (
        "S 2, M 4, L 0, XL 1; the line with a missing size is not counted; got %s" % out["orders"].tolist())


def test_all_unused():
    df = pd.DataFrame({"order_id": [1], "size": pd.Series([None], dtype=SIZES)})
    out = orders_per_size(df)
    assert out["orders"].tolist() == [0, 0, 0, 0], "no valid size at all: every size is listed with 0"


def test_input_unchanged():
    df = lines()
    before = df.copy()
    orders_per_size(df)
    pd.testing.assert_frame_equal(df, before, obj="the order lines")
