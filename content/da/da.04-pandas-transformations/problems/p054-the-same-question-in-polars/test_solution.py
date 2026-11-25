import random

import pandas as pd
import polars as pl
import pytest

from solution import revenue_by_region_pl


def data():
    return {
        "order_id": [10001, 10001, 10002, 10003, 10004, 10004, 10005, 10006, 10007],
        "region": ["north", "north", "north", "west", "west", "west", "south", "east", "east"],
        "channel": ["store", "store", "online", "store", "online", "online", "store", "store", "online"],
        "revenue": [100.0, 50.0, 150.0, 200.0, 60.0, 40.0, 120.0, 20.0, 30.0],
    }


def pandas_answer(d):
    df = pd.DataFrame(d)
    out = (df.groupby("region", as_index=False)
             .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
             .sort_values(["revenue", "region"], ascending=[False, True]))
    return out.to_dict("records")


def test_returns_polars_frame_with_columns():
    out = revenue_by_region_pl(pl.DataFrame(data()))
    assert isinstance(out, pl.DataFrame), "return a Polars DataFrame (not pandas, not a LazyFrame)"
    assert out.columns == ["region", "revenue", "orders"], "columns region, revenue, orders; got %s (alias the count?)" % out.columns


def test_values_and_order():
    got = revenue_by_region_pl(pl.DataFrame(data())).to_dicts()
    assert [r["region"] for r in got] == ["north", "west", "south", "east"], (
        "sorted by revenue descending; north and west both have 300, so the tie goes alphabetically (north first); got %s"
        % [r["region"] for r in got])
    by = {r["region"]: r for r in got}
    assert by["north"]["orders"] == 2, "north has 3 lines but only 2 distinct orders: use n_unique, not a line count"
    assert by["west"]["orders"] == 2 and by["east"]["orders"] == 2
    assert by["north"]["revenue"] == pytest.approx(300.0)


def test_equals_pandas_answer():
    got = revenue_by_region_pl(pl.DataFrame(data())).to_dicts()
    want = pandas_answer(data())
    assert got == want, "the Polars table must equal the pandas answer row by row:\n%s\n%s" % (got, want)


@pytest.mark.parametrize("seed", range(5))
def test_random_against_pandas(seed):
    rng = random.Random(seed)
    n = rng.randint(5, 80)
    d = {
        "order_id": [rng.randint(1, n // 2 + 1) for _ in range(n)],
        "region": [rng.choice(["north", "west", "south", "east", "central"]) for _ in range(n)],
        "channel": [rng.choice(["store", "online"]) for _ in range(n)],
        "revenue": [round(rng.uniform(40, 900), 2) for _ in range(n)],
    }
    got = revenue_by_region_pl(pl.DataFrame(d)).to_dicts()
    want = pandas_answer(d)
    assert [r["region"] for r in got] == [r["region"] for r in want], "region order differs from pandas (seed %d)" % seed
    assert [r["orders"] for r in got] == [r["orders"] for r in want], "distinct order counts differ (seed %d)" % seed
    assert [r["revenue"] for r in got] == pytest.approx([r["revenue"] for r in want]), "revenue differs (seed %d)" % seed


def test_input_unchanged():
    items = pl.DataFrame(data())
    before = items.clone()
    revenue_by_region_pl(items)
    assert items.equals(before), "do not change the input frame"
