import pandas as pd

from solution import attach_store_names

COLUMNS = ["order_id", "customer_id", "store_id", "city_customer", "city_store", "region"]


def orders():
    return pd.DataFrame({
        "order_id": [101, 102, 103, 104, 105, 106],
        "customer_id": ["C1", "C2", "C3", "C1", "C4", "C2"],
        "store_id": ["S3", "S1", "S2", "S7", "S1", "S3"],
        "city": ["Pune", "Agra", "Delhi", "Pune", "Surat", "Agra"],
    }, index=[3, 1, 4, 1, 5, 9])


def stores():
    return pd.DataFrame({
        "sid": ["S1", "S2", "S3", "S4"],
        "city": ["Pune", "Delhi", "Agra", "Jaipur"],
        "region": ["west", "north", "north", "north"],
    })


def result():
    return attach_store_names(orders(), stores())


def test_columns():
    out = result()
    assert list(out.columns) == COLUMNS, (
        "columns must be %s. Got %s. Use suffixes=('_customer', '_store') and drop the extra key column 'sid'."
        % (COLUMNS, list(out.columns)))


def test_row_count_and_order():
    out = result()
    assert len(out) == 6, (
        "one row per order (6), got %d. A left join keeps every order; an inner join drops order 104 whose store "
        "S7 is unknown." % len(out))
    assert out["order_id"].tolist() == [101, 102, 103, 104, 105, 106], "original order of the orders."
    assert out.index.tolist() == list(range(6)), "index 0..n-1."


def test_cities_not_mixed_up():
    out = result()
    assert out["city_customer"].tolist() == ["Pune", "Agra", "Delhi", "Pune", "Surat", "Agra"], (
        "city_customer must be the order table's city (the customer's), unchanged.")
    assert out["city_store"].tolist()[:3] == ["Agra", "Pune", "Delhi"], (
        "city_store must come from stores: S3 is in Agra, S1 in Pune, S2 in Delhi.")
    assert out["region"].tolist()[:3] == ["north", "west", "north"]


def test_unknown_store_kept():
    out = result().set_index("order_id")
    assert pd.isna(out.loc[104, "city_store"]) and pd.isna(out.loc[104, "region"]), (
        "order 104 is from store S7, which is not in stores: keep it with missing city_store and region.")


def test_inputs_not_changed():
    o, s = orders(), stores()
    ob, sb = o.copy(), s.copy()
    attach_store_names(o, s)
    pd.testing.assert_frame_equal(o, ob, obj="the input orders")
    pd.testing.assert_frame_equal(s, sb, obj="the input stores (rename a copy if you rename)")
