import pandas as pd

from solution import orders_with_customers


def orders():
    return pd.DataFrame({
        "order_id": [10001, 10002, 10003, 10004, 10005, 10006, 10007, 10008],
        "customer_id": ["C3", "C1", "C9", "C3", "C2", "C9", "C1", "C3"],
        "store_id": ["S1", "S2", "S1", "S3", "S1", "S2", "S2", "S1"],
    }, index=[5, 6, 7, 8, 9, 10, 11, 12])


def customers():
    return pd.DataFrame({
        "customer_id": ["C1", "C2", "C3", "C4"],
        "city": ["Pune", "Delhi", "Agra", "Surat"],
        "segment": ["retail", "premium", "retail", "business"],
    })


def test_row_count_equals_orders():
    df = orders()
    table, _ = orders_with_customers(df, customers())
    assert len(table) == len(df), (
        "golden rule: a left join from orders to a table with unique customer ids keeps exactly one row per order "
        "(%d), got %d. An inner join drops the orphan orders; a right join adds customers without orders."
        % (len(df), len(table)))


def test_every_order_in_original_order():
    table, _ = orders_with_customers(orders(), customers())
    assert table["order_id"].tolist() == orders()["order_id"].tolist(), "every order, in the original order."
    assert table.index.tolist() == list(range(8)), "index 0..n-1."
    assert list(table.columns) == ["order_id", "customer_id", "store_id", "city", "segment"], (
        "columns: the order columns, then city and segment (no _merge column left over). Got %s." % list(table.columns))


def test_customer_details_attached():
    table, _ = orders_with_customers(orders(), customers())
    assert table["city"].tolist()[:2] == ["Agra", "Pune"], "C3 lives in Agra, C1 in Pune."
    assert table["segment"].tolist()[4] == "premium", "C2 is premium."


def test_orphans_kept_with_missing_details():
    table, _ = orders_with_customers(orders(), customers())
    orphans = table[table["customer_id"] == "C9"]
    assert len(orphans) == 2, "the two orders of the unknown customer C9 must be kept."
    assert orphans["city"].isna().all() and orphans["segment"].isna().all(), "an unknown customer has missing city and segment."


def test_unknown_count():
    _, unknown = orders_with_customers(orders(), customers())
    assert type(unknown) is int, "unknown must be a plain int: wrap the count in int(...)."
    assert unknown == 2, (
        "2 orders (both C9) have no customer row. C4 has no orders, but that does not count: the question is about "
        "orders. Got %s." % unknown)


def test_no_orphans():
    df = orders()
    df = df[df["customer_id"] != "C9"]
    table, unknown = orders_with_customers(df, customers())
    assert unknown == 0 and len(table) == 6, "without orphans nothing is unknown and the count is still one row per order."


def test_inputs_not_changed():
    o, c = orders(), customers()
    ob, cb = o.copy(), c.copy()
    orders_with_customers(o, c)
    pd.testing.assert_frame_equal(o, ob, obj="the input orders")
    pd.testing.assert_frame_equal(c, cb, obj="the input customers")
