import pandas as pd

from solution import sales_by_region, sales_for


def frame():
    return pd.DataFrame({
        "region": ["S", "N", "N", "S", "W"],
        "month": ["Jan", "Jan", "Feb", "Feb", "Mar"],
        "sales": [7, 10, 12, 5, 3],
    })


def test_existing_pairs():
    df = frame()
    assert sales_for(df, "N", "Feb") == 12, "(N, Feb) is 12: .loc[(region, month), 'sales'] on the two-level index."
    assert sales_for(df, "S", "Jan") == 7
    assert type(sales_for(df, "W", "Mar")) is int, "return int(...), not a numpy integer."


def test_missing_pair_is_zero_not_keyerror():
    df = frame()
    assert sales_for(df, "N", "Mar") == 0, "region N exists but not in March: the answer is 0, catch the KeyError."
    assert sales_for(df, "X", "Jan") == 0, "an unknown region must also give 0."
    assert sales_for(df, "Jan", "N") == 0, "the levels are (region, month); swapping them finds nothing."


def test_sales_by_region_sums_the_inner_level():
    df = frame()
    out = sales_by_region(df)
    assert out == {"N": 22, "S": 12, "W": 3}, "sum the months inside each region: got %s." % out
    assert list(out) == ["N", "S", "W"], "regions must come in sorted order, got %s." % list(out)
    assert all(type(v) is int for v in out.values()), "totals must be plain ints."


def test_single_row_region():
    df = pd.DataFrame({"region": ["Z"], "month": ["Jan"], "sales": [4]})
    assert sales_by_region(df) == {"Z": 4}, "a region with one month: .loc[region, 'sales'] may be a scalar, not a Series."


def test_matches_plain_masks_on_bigger_data():
    months = ["Jan", "Feb", "Mar", "Apr"]
    rows = [(r, m, 10 * i + j) for i, r in enumerate("EWNS") for j, m in enumerate(months)]
    df = pd.DataFrame(rows, columns=["region", "month", "sales"])
    got = sales_by_region(df)
    for r in "EWNS":
        assert got[r] == int(df.loc[df["region"] == r, "sales"].sum()), "total for region %s differs from the filter-and-sum answer." % r
    for r, m, v in rows:
        assert sales_for(df, r, m) == v


def test_input_not_changed():
    df = frame()
    before = df.copy()
    sales_for(df, "N", "Jan")
    sales_by_region(df)
    pd.testing.assert_frame_equal(df, before, obj="the input frame (do not set_index in place)")
