import math

import numpy as np
import pandas as pd
import pytest

from solution import (average_order_value, channel_share, repeat_customer_share, returns_rate,
                      revenue_by_month, top_products)


def tiny():
    return pd.DataFrame({
        "order_date": pd.to_datetime(["2025-01-05", "2025-01-20", "2025-03-02", "2025-03-09", "2025-03-09"]),
        "customer": ["A", "B", "A", "C", "A"],
        "product": ["tea", "tea", "rice", "tea", "rice"],
        "channel": ["web", "shop", "web", "web", "shop"],
        "qty": [2, 1, 3, 1, 2],
        "unit_price": [100.0, 100.0, 50.0, 100.0, 50.0],
        "returned": [False, False, False, True, False],
    })


def make(n=400, seed=58):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "order_date": pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 150, n), unit="D"),
        "customer": rng.choice([f"cust{i:02d}" for i in range(60)], n),
        "product": rng.choice(["tea", "rice", "novel", "atlas", "puzzle", "spade", "hose"], n),
        "channel": rng.choice(["web", "shop", "phone"], n, p=[0.5, 0.4, 0.1]),
        "qty": rng.integers(1, 8, n),
        "unit_price": rng.integers(10, 500, n) / 4,
        "returned": rng.random(n) < 0.12,
    })


def rows(df):
    return list(df.itertuples(index=False))


# ---- slow plain-Python versions ----

def slow_revenue_by_month(df):
    rs = rows(df)
    first = min(r.order_date for r in rs)
    last = max(r.order_date for r in rs)
    months, y, m = [], first.year, first.month
    while (y, m) <= (last.year, last.month):
        months.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    totals = {k: 0.0 for k in months}
    for r in rs:
        if not r.returned:
            totals[f"{r.order_date.year:04d}-{r.order_date.month:02d}"] += r.qty * r.unit_price
    return totals


def slow_counts(df, col):
    out = {}
    for r in rows(df):
        if not r.returned:
            key = getattr(r, col)
            out[key] = out.get(key, 0) + 1
    return out


def test_tiny_example_by_hand():
    df = tiny()
    before = df.copy()
    rev = revenue_by_month(df)
    assert isinstance(rev, pd.Series), f"revenue_by_month returns a Series, not a {type(rev).__name__}."
    assert rev.index.tolist() == ["2025-01", "2025-02", "2025-03"], f"every month from the first to the last order, even one without orders: ['2025-01', '2025-02', '2025-03'], got {rev.index.tolist()}."
    assert rev.tolist() == [300.0, 0.0, 250.0], f"Jan: 200 + 100; Feb: none; Mar: 150 + 100 (the returned order of 100 does not count). Got {rev.tolist()}."
    assert top_products(df, n=2) == [("rice", 2), ("tea", 2)], f"non-returned orders per product: rice 2, tea 2 (tie: A to Z); got {top_products(df, n=2)}."
    assert channel_share(df) == pytest.approx({"web": 0.5, "shop": 0.5}), f"4 sales: web 2, shop 2; got {channel_share(df)}."
    assert average_order_value(df) == pytest.approx(550 / 4), f"revenue 550 / 4 sales = 137.5; got {average_order_value(df)}."
    assert repeat_customer_share(df) == pytest.approx(1 / 2), f"customers with a sale: A (3 sales), B (1): half have two or more; C only had a returned order and does not count. Got {repeat_customer_share(df)}."
    assert returns_rate(df) == pytest.approx(1 / 5), f"1 of 5 orders returned = 0.2 (all orders are the base); got {returns_rate(df)}."
    pd.testing.assert_frame_equal(df, before, obj="the input frame")


def test_types():
    df = make()
    assert isinstance(average_order_value(df), float) and isinstance(returns_rate(df), float) and isinstance(repeat_customer_share(df), float), (
        "the three single numbers must be plain floats")
    top = top_products(df)
    assert isinstance(top, list) and all(isinstance(p, tuple) and isinstance(p[1], int) for p in top), "top_products returns a list of (product, int) pairs."
    assert isinstance(channel_share(df), dict), "channel_share returns a dict."


def test_revenue_by_month_against_the_slow_loop():
    for seed in (1, 2, 3):
        df = make(seed=seed)
        got = revenue_by_month(df)
        want = slow_revenue_by_month(df)
        assert got.index.tolist() == list(want), f"month labels differ: expected {list(want)}, got {got.index.tolist()}."
        assert got.tolist() == pytest.approx(list(want.values())), f"monthly revenue differs from the plain loop (seed {seed})."


def test_top_products_and_channels_against_the_slow_loop():
    df = make()
    counts = slow_counts(df, "product")
    want = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    assert top_products(df, n=5) == want[:5], f"top 5 products: expected {want[:5]}, got {top_products(df, n=5)}. Ties are ordered by name."
    assert top_products(df, n=3) == want[:3], "n must change the length of the list."
    shares = channel_share(df)
    total = sum(slow_counts(df, "channel").values())
    assert shares == pytest.approx({k: v / total for k, v in slow_counts(df, "channel").items()}), "channel shares are shares of NON-returned orders."
    assert sum(shares.values()) == pytest.approx(1.0), "the shares must add up to 1."


def test_single_numbers_against_the_slow_loop():
    for seed in (4, 5):
        df = make(seed=seed)
        sales = [r for r in rows(df) if not r.returned]
        revenue = sum(r.qty * r.unit_price for r in sales)
        assert average_order_value(df) == pytest.approx(revenue / len(sales)), "average order value = revenue of sales / number of sales (not of all rows)."
        per_customer = {}
        for r in sales:
            per_customer[r.customer] = per_customer.get(r.customer, 0) + 1
        assert repeat_customer_share(df) == pytest.approx(sum(1 for v in per_customer.values() if v >= 2) / len(per_customer)), (
            "repeat share = customers with 2+ non-returned orders / customers with at least one non-returned order.")
        assert returns_rate(df) == pytest.approx(sum(1 for r in rows(df) if r.returned) / len(df)), "returns rate uses ALL orders as the base."


def test_the_returned_column_matters():
    df = tiny().assign(returned=False)
    assert returns_rate(df) == 0.0 and revenue_by_month(df).tolist() == [300.0, 0.0, 350.0], "with nothing returned, every order counts."
