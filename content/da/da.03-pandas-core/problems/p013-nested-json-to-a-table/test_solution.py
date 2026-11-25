import copy

import pandas as pd

from solution import orders_from_json

RECORDS = [
    {"id": 1, "customer": {"name": "Asha", "city": "Pune"}, "items": [{"sku": "A", "qty": 2}, {"sku": "B", "qty": 1}]},
    {"id": 2, "customer": {"name": "Ben"}, "items": [{"sku": "A", "qty": 5}]},
    {"id": 3, "customer": {"name": "Chen"}, "items": []},
    {"id": 4, "items": [{"sku": "C", "qty": 7}, {"sku": "D"}]},
    {"id": 5, "customer": {"city": "Agra"}, "items": [{"sku": "A", "qty": 1}]},
]


def plain_rows(records):
    rows = []
    for order in records:
        name = order.get("customer", {}).get("name")
        for item in order.get("items", []):
            rows.append((order["id"], name, item.get("sku"), item.get("qty")))
    return rows


def test_columns_and_row_count():
    out = orders_from_json(RECORDS)
    assert out.columns.tolist() == ["id", "customer", "sku", "qty"], (
        "columns must be id, customer, sku, qty (rename 'customer.name'); got %s." % out.columns.tolist())
    assert len(out) == 6, "one row per item: 2 + 1 + 0 + 2 + 1 = 6 rows (an order with no items gives none). Got %d." % len(out)
    assert out.index.tolist() == list(range(6))


def test_values_match_a_plain_loop():
    out = orders_from_json(RECORDS)
    want = plain_rows(RECORDS)
    got = [tuple(None if pd.isna(v) else v for v in row) for row in out.itertuples(index=False, name=None)]
    want = [tuple(None if v is None else v for v in row) for row in want]
    assert len(got) == len(want)
    for g, w in zip(got, want):
        assert g[0] == w[0], "id repeated per line: got %r, expected %r." % (g, w)
        assert g[1] == w[1], "customer name differs on row %r (missing name must be missing, not an error)." % (g,)
        assert g[2] == w[2], "sku differs on row %r." % (g,)
        assert (g[3] is None and w[3] is None) or float(g[3]) == float(w[3]), "qty differs on row %r (a missing qty stays missing)." % (g,)


def test_missing_nested_keys_do_not_raise():
    only = [{"id": 9, "items": [{"sku": "Z"}]}]
    out = orders_from_json(only)
    assert len(out) == 1, "an order without customer and an item without qty still gives one row."
    assert pd.isna(out["customer"].iloc[0]) and pd.isna(out["qty"].iloc[0]), "the missing cells must be missing values."
    assert out["id"].iloc[0] == 9 and out["sku"].iloc[0] == "Z"


def test_id_dtype_and_order():
    out = orders_from_json(RECORDS)
    assert str(out["id"].dtype) == "int64", "id dtype is %s; convert with astype('int64')." % out["id"].dtype
    assert out["id"].tolist() == [1, 1, 2, 4, 4, 5], "lines must follow the input order, ids repeated per item."


def test_input_not_changed():
    before = copy.deepcopy(RECORDS)
    orders_from_json(RECORDS)
    assert RECORDS == before, "the list of records must not be modified."
