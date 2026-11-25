import pandas as pd

from solution import bought_product


def customers():
    return pd.DataFrame({
        "customer_id": ["C4", "C1", "C3", "C2", "C5"],
        "city": ["Jaipur", "Pune", "Agra", "Delhi", "Surat"],
        "segment": ["retail", "premium", "retail", "business", "retail"],
    })


def lines():
    return pd.DataFrame({
        "order_id": [1, 1, 2, 3, 4, 5, 6, 7, 8],
        "customer_id": ["C3", "C3", "C1", "C3", "C2", "C3", "C1", "C9", "C2"],
        "product_id": ["P7", "P2", "P2", "P7", "P5", "P7", "P7", "P5", "P2"],
        "qty": [1, 2, 1, 1, 3, 1, 2, 1, 1],
    })


def test_buyers_once_each():
    out = bought_product(customers(), lines(), "P7")
    assert out["customer_id"].tolist() == ["C1", "C3"], (
        "C3 bought P7 three times and C1 once: each appears ONCE, in the customer table's order. A merge of customers "
        "with the lines repeats C3 three times. Got %s." % out["customer_id"].tolist())


def test_only_customer_columns():
    out = bought_product(customers(), lines(), "P7")
    assert list(out.columns) == ["customer_id", "city", "segment"], (
        "only the customer columns (no order_id, product_id, qty). Got %s." % list(out.columns))
    assert out.index.tolist() == [0, 1], "index 0..n-1."


def test_row_count_never_exceeds_customers():
    c = customers()
    for pid in ["P2", "P5", "P7"]:
        out = bought_product(c, lines(), pid)
        assert len(out) <= len(c), "a semi-join can never return more rows than the customer table."
        assert out["customer_id"].is_unique, "%s: each customer at most once." % pid


def test_orphan_buyer_is_not_a_customer():
    out = bought_product(customers(), lines(), "P5")
    assert out["customer_id"].tolist() == ["C2"], "P5 was bought by C2 and by the unknown C9: only C2 is a customer."


def test_nobody_bought_it():
    out = bought_product(customers(), lines(), "P99")
    assert len(out) == 0, "nobody bought P99: empty result."
    assert list(out.columns) == ["customer_id", "city", "segment"], "an empty result keeps the customer columns."


def test_inputs_not_changed():
    c, l = customers(), lines()
    cb, lb = c.copy(), l.copy()
    bought_product(c, l, "P7")
    pd.testing.assert_frame_equal(c, cb, obj="the input customers")
    pd.testing.assert_frame_equal(l, lb, obj="the input lines")
