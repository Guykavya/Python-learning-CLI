import random

import pandas as pd
import polars as pl
import pytest

from solution import top_products_lazy

ITEMS = {
    "order_id": [10001, 10001, 10002, 10002, 10003, 10003, 10004],
    "product_id": ["P1", "P2", "P1", "P3", "P4", "P6", "P9"],
    "qty": [2, 1, 1, 5, 1, 2, 1],
    "unit_price": [10.0, 30.0, 10.0, 2.0, 15.0, 8.0, 99.0],
}
PRODUCTS = {
    "product_id": ["P1", "P2", "P3", "P4", "P5", "P6"],
    "category": ["grocery", "grocery", "grocery", "toys", "toys", "home"],
    "list_price": [10.0, 30.0, 2.0, 15.0, 40.0, 8.0],
}


def pandas_answer(items, products, n):
    i, p = pd.DataFrame(items), pd.DataFrame(products)
    m = i.merge(p, on="product_id", how="inner", validate="m:1")
    m["revenue"] = m["qty"] * m["unit_price"]
    s = m.groupby(["category", "product_id"], as_index=False)["revenue"].sum()
    s = s.sort_values(["category", "revenue", "product_id"], ascending=[True, False, True])
    return s.groupby("category").head(n)[["category", "product_id", "revenue"]].to_dict("records")


def test_returns_a_lazy_plan():
    plan = top_products_lazy(pl.LazyFrame(ITEMS), pl.LazyFrame(PRODUCTS))
    assert isinstance(plan, pl.LazyFrame), "return the LazyFrame plan; do not call collect() inside the function (got %s)" % type(plan).__name__


def test_fixed_result():
    got = top_products_lazy(pl.LazyFrame(ITEMS), pl.LazyFrame(PRODUCTS), n=2).collect()
    assert got.columns == ["category", "product_id", "revenue"], "columns category, product_id, revenue; got %s" % got.columns
    rows = [(r["category"], r["product_id"], r["revenue"]) for r in got.to_dicts()]
    assert ("unknown", "P9") not in [(c, p) for c, p, _ in rows] and all(c is not None for c, _, _ in rows), (
        "the line for P9 has no product: an INNER join leaves it out (no null category)")
    assert rows == [("grocery", "P1", 30.0), ("grocery", "P2", 30.0), ("home", "P6", 16.0), ("toys", "P4", 15.0)], (
        "grocery: P1 = 2x10 + 1x10 = 30 ties with P2 = 30 (P1 first by id), P3 = 10 is third and dropped; "
        "home and toys have one sold product each; sorted by category. Got %s" % rows)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_equals_pandas(n):
    got = top_products_lazy(pl.LazyFrame(ITEMS), pl.LazyFrame(PRODUCTS), n=n).collect().to_dicts()
    assert got == pandas_answer(ITEMS, PRODUCTS, n), "the collected result must equal the pandas answer for n=%d" % n


@pytest.mark.parametrize("seed", range(4))
def test_random_against_pandas(seed):
    rng = random.Random(seed)
    pids = ["P%02d" % k for k in range(1, 13)]
    products = {"product_id": pids, "category": [rng.choice(["home", "toys", "office"]) for _ in pids],
                "list_price": [float(rng.randint(40, 900)) for _ in pids]}
    m = rng.randint(5, 60)
    items = {"order_id": [rng.randint(1, 30) for _ in range(m)], "product_id": [rng.choice(pids) for _ in range(m)],
             "qty": [rng.randint(1, 5) for _ in range(m)], "unit_price": [float(rng.randint(1, 50)) for _ in range(m)]}
    got = top_products_lazy(pl.LazyFrame(items), pl.LazyFrame(products), n=3).collect().to_dicts()
    assert got == pandas_answer(items, products, 3), "differs from the pandas answer (seed %d)" % seed


def test_duplicate_product_is_refused():
    dup = {k: v + [v[0]] for k, v in PRODUCTS.items()}
    plan = top_products_lazy(pl.LazyFrame(ITEMS), pl.LazyFrame(dup))
    try:
        plan.collect()
    except Exception as err:
        assert "m:1" in str(err) or "validation" in str(err), "expected the m:1 validation error, got %r" % err
    else:
        pytest.fail("a duplicated product row must make the join fail at collect(): pass validate='m:1' to join "
                    "(otherwise that product's revenue is silently doubled)")
