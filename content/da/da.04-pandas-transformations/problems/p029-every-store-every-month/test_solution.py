import random

import pandas as pd

from solution import full_grid

MONTHS = ["2025-01", "2025-02", "2025-03"]


def stores():
    return pd.DataFrame({
        "store_id": ["S3", "S1", "S2"],
        "store_city": ["Agra", "Pune", "Delhi"],
        "region": ["north", "west", "north"],
    })


def sales():
    return pd.DataFrame({
        "store_id": ["S1", "S1", "S2", "S3", "S1", "S9"],
        "month": ["2025-03", "2025-01", "2025-02", "2024-12", "2025-02", "2025-01"],
        "revenue": [30.0, 10.0, 25.0, 99.0, 20.0, 5.0],
    })


def result():
    return full_grid(sales(), stores(), MONTHS)


def test_row_count_is_stores_times_months():
    out = result()
    assert len(out) == 9, (
        "the grid has 3 stores x 3 months = 9 rows, got %d. Build it with a cross join "
        "(stores[['store_id']].merge(months_frame, how='cross')), then LEFT-join the sales onto it." % len(out))
    assert list(out.columns) == ["store_id", "month", "revenue"], "columns: store_id, month, revenue. Got %s." % list(out.columns)


def test_sorted_and_reindexed():
    out = result()
    assert out["store_id"].tolist() == ["S1"] * 3 + ["S2"] * 3 + ["S3"] * 3, "sorted by store_id, then month."
    assert out["month"].tolist() == MONTHS * 3
    assert out.index.tolist() == list(range(9)), "index 0..n-1."


def test_revenue_and_zeros():
    got = result()["revenue"].tolist()
    assert got == [10.0, 20.0, 30.0, 0.0, 25.0, 0.0, 0.0, 0.0, 0.0], (
        "revenue from the sales of that store and month, 0.0 where there was none (fillna(0)). S3 sold only in "
        "2024-12, which is outside the grid. Got %s." % got)
    assert not result()["revenue"].isna().any(), "no missing revenue: an empty cell of the grid is 0.0."


def test_sales_outside_the_grid_left_out():
    out = result()
    assert "S9" not in set(out["store_id"]), "S9 is not in stores: the grid comes from stores, so S9 has no row."
    assert "2024-12" not in set(out["month"]), "2024-12 is not in months: no row for it."


def test_random_against_a_loop():
    rnd = random.Random(29)
    st = pd.DataFrame({"store_id": ["S%d" % i for i in range(1, 7)], "store_city": ["x"] * 6, "region": ["r"] * 6})
    months = ["2025-%02d" % m for m in range(1, 13)]
    pairs = rnd.sample([(s, m) for s in st["store_id"] for m in months], 40)
    sa = pd.DataFrame({"store_id": [p[0] for p in pairs], "month": [p[1] for p in pairs],
                       "revenue": [float(rnd.randint(1, 500)) for _ in pairs]})
    lookup = {(s, m): r for s, m, r in zip(sa["store_id"], sa["month"], sa["revenue"])}
    want = [lookup.get((s, m), 0.0) for s in sorted(st["store_id"]) for m in months]
    out = full_grid(sa, st, months)
    assert len(out) == 72, "6 stores x 12 months = 72 rows."
    assert out["revenue"].tolist() == want, "the grid differs from a plain double loop over stores and months."


def test_inputs_not_changed():
    s, st = sales(), stores()
    sb, stb = s.copy(), st.copy()
    full_grid(s, st, list(MONTHS))
    pd.testing.assert_frame_equal(s, sb, obj="the input sales")
    pd.testing.assert_frame_equal(st, stb, obj="the input stores")
