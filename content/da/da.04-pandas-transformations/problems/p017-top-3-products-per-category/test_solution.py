import random

import pandas as pd
import pytest

from solution import top_products


def products():
    return pd.DataFrame({
        "product_id": ["P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08"],
        "category": ["home", "home", "home", "home", "toys", "toys", "office", "grocery"],
        "list_price": [60.0, 100.0, 100.0, 50.0, 10.0, 40.0, 25.0, 2.0],
    })


def lines():
    # revenue: P01 100 (two lines), P02 300, P03 100, P04 50, P05 20, P06 40, P08 10; P07 never sold
    return pd.DataFrame({
        "order_id": [1, 1, 2, 2, 3, 4, 5, 6],
        "product_id": ["P03", "P04", "P01", "P02", "P05", "P01", "P06", "P08"],
        "qty": [1, 1, 1, 3, 2, 2, 1, 5],
        "unit_price": [100.0, 50.0, 60.0, 100.0, 10.0, 20.0, 40.0, 2.0],
    })


def result(n=3):
    out = top_products(lines(), products(), n=n)
    assert list(out.columns) == ["category", "product_id", "revenue", "rank"], (
        "columns must be category, product_id, revenue, rank. Got %s." % list(out.columns))
    return out


def test_rows_and_order():
    out = result()
    got = list(zip(out["category"], out["product_id"]))
    assert got == [("grocery", "P08"), ("home", "P02"), ("home", "P01"), ("home", "P03"),
                   ("toys", "P06"), ("toys", "P05")], (
        "expected the top 3 of each category, sorted by category then rank. Got %s." % got)
    assert out.index.tolist() == list(range(6)), "index 0..n-1."


def test_ties_broken_by_product_id():
    out = result()
    home = out[out["category"] == "home"]
    assert home["product_id"].tolist() == ["P02", "P01", "P03"], (
        "P01 and P03 both made 100: the smaller id (P01) ranks first. Sort by revenue descending AND product_id "
        "ascending, so the tie rule does not depend on the order the rows happen to have.")
    assert home["rank"].tolist() == [1, 2, 3], "ranks are 1, 2, 3 with no repeats, even for a tie."


def test_revenue_and_rank_values():
    out = result()
    assert out["revenue"].tolist() == pytest.approx([10.0, 300.0, 100.0, 100.0, 40.0, 20.0]), (
        "revenue of a product = sum of qty * unit_price over ALL its lines (P01 has two lines: 60 + 40).")
    assert out["rank"].tolist() == [1, 1, 2, 3, 1, 2], "rank restarts at 1 in every category."
    assert pd.api.types.is_integer_dtype(out["rank"]), "rank must be an integer column (1, 2, 3), not 1.0."


def test_small_categories_and_unsold_products():
    out = result()
    assert (out["category"] == "toys").sum() == 2, "toys has only 2 sold products: show both, do not pad."
    assert "office" not in set(out["category"]), "P07 (office) never sold, so office has no row."
    assert "P04" not in set(out["product_id"]), "P04 is the 4th of home: outside the top 3."


def test_other_n():
    out = result(n=1)
    assert out["product_id"].tolist() == ["P08", "P02", "P06"], "n=1: the single best product of each category."


def slow_top(lines_df, products_df, n):
    cat = dict(zip(products_df["product_id"], products_df["category"]))
    rev = {}
    for pid, q, p in zip(lines_df["product_id"], lines_df["qty"], lines_df["unit_price"]):
        rev[pid] = rev.get(pid, 0.0) + q * p
    by_cat = {}
    for pid, r in rev.items():
        by_cat.setdefault(cat[pid], []).append((-r, pid))
    rows = []
    for c in sorted(by_cat):
        for k, (neg, pid) in enumerate(sorted(by_cat[c])[:n], start=1):
            rows.append((c, pid, -neg, k))
    return rows


def test_random_against_a_loop():
    rnd = random.Random(17)
    prods = pd.DataFrame({"product_id": ["P%02d" % i for i in range(30)],
                          "category": [rnd.choice(["a", "b", "c", "d"]) for _ in range(30)],
                          "list_price": [1.0] * 30})
    m = 300
    ls = pd.DataFrame({"order_id": range(m),
                       "product_id": [rnd.choice(prods["product_id"].tolist()[:26]) for _ in range(m)],
                       "qty": [rnd.randint(1, 3) for _ in range(m)],
                       "unit_price": [float(rnd.choice([5, 10, 20])) for _ in range(m)]})
    out = top_products(ls, prods, n=3)
    got = list(zip(out["category"], out["product_id"], out["revenue"], out["rank"]))
    want = slow_top(ls, prods, 3)
    assert [(c, p, k) for c, p, _, k in got] == [(c, p, k) for c, p, _, k in want], "differs from a plain loop."
    assert [r for _, _, r, _ in got] == pytest.approx([r for _, _, r, _ in want])


def test_inputs_not_changed():
    l, p = lines(), products()
    lb, pb = l.copy(), p.copy()
    top_products(l, p)
    pd.testing.assert_frame_equal(l, lb, obj="the input lines")
    pd.testing.assert_frame_equal(p, pb, obj="the input products")
