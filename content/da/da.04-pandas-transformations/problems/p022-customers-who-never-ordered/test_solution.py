import pandas as pd

from solution import never_ordered


def customers():
    return pd.DataFrame({
        "customer_id": ["C5", "C1", "C4", "C2", "C3", "C6"],
        "city": ["Surat", "Pune", "Jaipur", "Delhi", "Agra", "Mumbai"],
        "segment": ["retail", "premium", "retail", "business", "retail", "premium"],
    }, index=[30, 31, 32, 33, 34, 35])


def orders():
    return pd.DataFrame({
        "order_id": [1, 2, 3, 4, 5, 6, 7],
        "customer_id": ["C1", "C3", "C1", "C9", "C5", "C1", "C9"],
        "store_id": ["S1", "S2", "S1", "S3", "S1", "S2", "S1"],
    })


def test_the_right_customers():
    out = never_ordered(customers(), orders())
    assert out["customer_id"].tolist() == ["C4", "C2", "C6"], (
        "C4, C2 and C6 have no orders; keep them in the ORIGINAL customer order. Got %s." % out["customer_id"].tolist())


def test_only_customer_columns_and_no_duplicates():
    out = never_ordered(customers(), orders())
    assert list(out.columns) == ["customer_id", "city", "segment"], (
        "only the customer columns: no order columns and no _merge column. Got %s." % list(out.columns))
    assert out.index.tolist() == [0, 1, 2], "index 0..n-1."
    assert out["customer_id"].is_unique, "each customer at most once."


def test_orphan_orders_do_not_appear():
    out = never_ordered(customers(), orders())
    assert "C9" not in set(out["customer_id"]), "C9 is an orphan ORDER key, not a customer: it never belongs in the result."


def test_everybody_ordered():
    c = customers()
    o = pd.DataFrame({"order_id": range(6), "customer_id": c["customer_id"].tolist(), "store_id": ["S1"] * 6})
    out = never_ordered(c, o)
    assert len(out) == 0, "everybody ordered: empty result."
    assert list(out.columns) == ["customer_id", "city", "segment"], "an empty result keeps the customer columns."


def test_count_adds_up():
    c, o = customers(), orders()
    buyers = c["customer_id"].isin(o["customer_id"]).sum()
    assert len(never_ordered(c, o)) + buyers == len(c), "buyers + never-ordered must equal the number of customers."


def test_inputs_not_changed():
    c, o = customers(), orders()
    cb, ob = c.copy(), o.copy()
    never_ordered(c, o)
    pd.testing.assert_frame_equal(c, cb, obj="the input customers")
    pd.testing.assert_frame_equal(o, ob, obj="the input orders")
