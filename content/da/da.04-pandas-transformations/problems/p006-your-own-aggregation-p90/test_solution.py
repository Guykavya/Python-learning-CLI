import math
import random

import pandas as pd
import pytest

from solution import p90_delivery_days


def orders():
    nan = float("nan")
    rows = [("north", float(d)) for d in [7, 3, 10, 1, 5, 9, 2, 8, 4, 6]]
    rows += [("south", 4.0)]
    rows += [("west", 2.0), ("west", 6.0), ("west", nan), ("west", 3.0)]
    rows += [("east", nan), ("east", nan)]
    return pd.DataFrame({
        "order_id": range(1, len(rows) + 1),
        "region": [r for r, _ in rows],
        "delivery_days": [d for _, d in rows],
    })


def result(df=None):
    out = p90_delivery_days(orders() if df is None else df)
    assert list(out.columns) == ["region", "delivered", "median_days", "p90_days"], (
        "columns must be region, delivered, median_days, p90_days. Got %s." % list(out.columns))
    return out.set_index("region")


def test_one_row_per_region_sorted():
    out = p90_delivery_days(orders())
    assert out["region"].tolist() == ["east", "north", "south", "west"], (
        "one row per region, sorted. 'east' has no delivered orders but must still appear.")
    assert out.index.tolist() == [0, 1, 2, 3], "flat result with index 0..n-1."


def test_delivered_counts_known_values():
    got = result()["delivered"].to_dict()
    assert got == {"east": 0, "north": 10, "south": 1, "west": 3}, (
        "delivered = number of known delivery_days: count(), not size() (west has one undelivered order). Got %s." % got)


def test_ten_values():
    r = result().loc["north"]
    assert r["median_days"] == pytest.approx(5.5), "median of 1..10 is 5.5 (the mean of the two middle values)."
    assert r["p90_days"] == pytest.approx(9.1), (
        "p90 of 1..10 with linear interpolation is 9.1 (position 0.9 * 9 = 8.1 in the sorted list). "
        "Did you take the max, or the 9th value?")


def test_group_of_one_value():
    r = result().loc["south"]
    assert r["median_days"] == 4.0 and r["p90_days"] == 4.0, "a group with one value: median and p90 are that value."


def test_missing_values_are_skipped():
    r = result().loc["west"]
    assert r["median_days"] == pytest.approx(3.0), "west: known values 2, 6, 3 -> median 3. Missing values are skipped."
    assert r["p90_days"] == pytest.approx(5.4), "west: p90 of 2, 3, 6 is 3 + 0.8 * 3 = 5.4."


def test_region_with_nothing_delivered():
    r = result().loc["east"]
    assert math.isnan(r["median_days"]) and math.isnan(r["p90_days"]), (
        "east has no known delivery time: its statistics are missing, not 0.")


def test_matches_quantile_on_random_data():
    rnd = random.Random(11)
    regions = ["north", "south", "east", "west", "central"]
    n = 300
    df = pd.DataFrame({
        "order_id": range(n),
        "region": [rnd.choice(regions) for _ in range(n)],
        "delivery_days": [float(rnd.randint(1, 15)) if rnd.random() > 0.1 else float("nan") for _ in range(n)],
    })
    out = result(df)
    for reg in regions:
        vals = sorted(v for r, v in zip(df["region"], df["delivery_days"]) if r == reg and not math.isnan(v))
        pos = 0.9 * (len(vals) - 1)
        lo = int(pos)
        hi = min(lo + 1, len(vals) - 1)
        slow = vals[lo] + (pos - lo) * (vals[hi] - vals[lo])
        assert out.loc[reg, "p90_days"] == pytest.approx(slow), "p90 of %s differs from linear interpolation." % reg
        assert out.loc[reg, "delivered"] == len(vals)


def test_input_not_changed():
    df = orders()
    before = df.copy()
    p90_delivery_days(df)
    pd.testing.assert_frame_equal(df, before, obj="the input orders")
