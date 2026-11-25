import pandas as pd
import pytest

from solution import net_revenue_by_category


def products():
    return pd.DataFrame({
        "product_id": ["P1", "P2", "P3", "P4", "P5"],
        "category": ["grocery", "grocery", "home", "toys", "home"],
        "list_price": [10.0, 5.0, 100.0, 30.0, 50.0],
    })


def lines():
    return pd.DataFrame({
        "order_id": [1, 1, 2, 3, 3, 4],
        "product_id": ["P1", "P3", "P2", "P1", "P5", "P3"],
        "qty": [2, 1, 3, 1, 2, 1],
        "unit_price": [10.0, 100.0, 5.0, 10.0, 50.0, 100.0],
        "discount": [0.0, 0.1, 0.0, 0.5, 0.2, 0.0],
    })


def result():
    out = net_revenue_by_category(lines(), products())
    assert list(out.columns) == ["category", "net_revenue"], "columns must be category, net_revenue. Got %s." % list(out.columns)
    return out


def test_categories_with_sales_only():
    out = result()
    assert out["category"].tolist() == ["grocery", "home"], (
        "one row per category that has lines, sorted. 'toys' (P4) sold nothing, so it has no row.")
    assert out.index.tolist() == [0, 1], "flat result with index 0..n-1."


def test_net_revenue_is_computed_per_line():
    got = result()["net_revenue"].tolist()
    assert got == pytest.approx([40.0, 270.0]), (
        "net revenue must be computed on EACH line before grouping: grocery = 2*10*1 + 3*5*1 + 1*10*0.5 = 40; "
        "home = 1*100*0.9 + 2*50*0.8 + 1*100*1 = 270. Multiplying group totals, sum(qty) * sum(unit_price) * (1 - mean discount), gives "
        "125 and 900. Got %s." % got)


def test_total_matches_the_lines():
    df = lines()
    line_total = (df["qty"] * df["unit_price"] * (1 - df["discount"])).sum()
    assert result()["net_revenue"].sum() == pytest.approx(line_total), (
        "the category totals must add up to the net revenue of all lines: no line lost or duplicated by the merge.")


def test_category_order_does_not_follow_product_order():
    p = products().iloc[::-1].reset_index(drop=True)
    out = net_revenue_by_category(lines(), p)
    assert out["net_revenue"].tolist() == pytest.approx([40.0, 270.0]), (
        "join by product_id, not by position: the product table may come in any order.")


def test_inputs_not_changed():
    l, p = lines(), products()
    lb, pb = l.copy(), p.copy()
    net_revenue_by_category(l, p)
    pd.testing.assert_frame_equal(l, lb, obj="the input lines")
    pd.testing.assert_frame_equal(p, pb, obj="the input products")
