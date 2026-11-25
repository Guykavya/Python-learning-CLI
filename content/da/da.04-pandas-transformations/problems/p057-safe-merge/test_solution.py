import pandas as pd
import pytest

from solution import safe_merge


def test_good_left_join_result_and_record(orders, customers):
    ledger = []
    out = safe_merge(orders, customers, on="customer_id", name="orders + customers", ledger=ledger)
    assert len(out) == len(orders), "a many-to-one left join keeps the 6 order rows"
    want = orders.merge(customers, on="customer_id", how="left")
    pd.testing.assert_frame_equal(out, want, obj="the merged frame (drop the _merge helper column)")
    assert len(ledger) == 1, "one record per call appended to the ledger list"
    r = ledger[0]
    assert r["step"] == "orders + customers", "step is the given name"
    assert (r["left_rows"], r["right_rows"], r["result_rows"]) == (6, 4, 6), "left_rows 6, right_rows 4, result_rows 6"
    assert r["unmatched_left"] == 2, "two orders found no customer: C9 (orphan) and the missing id (got %s)" % r["unmatched_left"]
    assert r["unmatched_keys"] == ["C9"], "unmatched_keys lists distinct NON-missing keys: ['C9'] (got %s)" % r["unmatched_keys"]
    assert r["null_keys_left"] == 1, "one order has a missing customer_id"
    assert "measure_before" not in r, "measure_before/after only when a measure is given"


def test_default_name_and_no_ledger(orders, customers):
    ledger = []
    safe_merge(orders, customers, on="customer_id", ledger=ledger)
    assert ledger[0]["step"] == "merge on ['customer_id']", "without a name, step is f'merge on {keys}'; got %r" % ledger[0]["step"]
    out = safe_merge(orders, customers, on="customer_id")
    assert len(out) == 6, "ledger=None must work too (nothing to append to)"


def test_validate_stops_a_wrong_relationship(orders, customers):
    dup = pd.concat([customers, customers.head(1)], ignore_index=True)
    with pytest.raises(pd.errors.MergeError):
        safe_merge(orders, dup, on="customer_id")


def test_row_guard_catches_fan_out(orders, customers):
    dup = pd.concat([customers, customers.head(1)], ignore_index=True)
    ledger = []
    with pytest.raises(AssertionError) as err:
        safe_merge(orders, dup, on="customer_id", validate=None, name="DUP", ledger=ledger)
    assert str(err.value).startswith("DUP: row count changed 6 -> 8"), (
        "C1 has 2 orders and now 2 customer rows: 6 -> 8. Message must be '<step>: row count changed 6 -> 8'; got %r" % str(err.value))
    assert len(ledger) == 1 and ledger[0]["result_rows"] == 8, "append the record BEFORE the checks so the failed step is logged"


def test_expect_same_rows_false_allows_growth(orders, customers):
    dup = pd.concat([customers, customers.head(1)], ignore_index=True)
    out = safe_merge(orders, dup, on="customer_id", validate=None, expect_same_rows=False)
    assert len(out) == 8, "with expect_same_rows=False and no measure, the fan-out is allowed (8 rows)"


def test_measure_unchanged_is_recorded(items, products):
    ledger = []
    out = safe_merge(items, products, on="product_id", measure="revenue", name="items + products", ledger=ledger)
    r = ledger[0]
    assert r["measure_before"] == 611.0 and r["measure_after"] == 611.0, (
        "measure_before/after are the revenue totals of left and result, rounded to 2: 611.0 both; got %s, %s"
        % (r.get("measure_before"), r.get("measure_after")))
    assert r["unmatched_keys"] == ["P9"], "P9 is not in products"
    assert len(out) == 7


def test_measure_guard_catches_lost_money_in_inner_join(items, products):
    ledger = []
    with pytest.raises(AssertionError) as err:
        safe_merge(items, products, on="product_id", how="inner", measure="revenue", name="inner", ledger=ledger)
    assert str(err.value).startswith("inner: revenue total changed 611.0 -> 531.0"), (
        "the inner join drops the P9 line (80.0): the measure guard must fire for ANY how; "
        "message '<step>: revenue total changed 611.0 -> 531.0'; got %r" % str(err.value))
    assert ledger[0]["result_rows"] == 6


def test_measure_guard_catches_fan_out_even_when_rows_may_grow(items, products):
    dup = pd.concat([products, products.iloc[[0]]], ignore_index=True)
    with pytest.raises(AssertionError) as err:
        safe_merge(items, dup, on="product_id", validate=None, measure="revenue", expect_same_rows=False, name="dup")
    assert "revenue total changed" in str(err.value), (
        "P1 is duplicated: its lines (200 + 100) count twice, so the money guard must fire; got %r" % str(err.value))


def test_two_key_columns(items, returns):
    ledger = []
    out = safe_merge(items, returns, on=["order_id", "product_id"], validate="1:1", measure="revenue", ledger=ledger)
    r = ledger[0]
    assert r["step"] == "merge on ['order_id', 'product_id']"
    assert r["unmatched_left"] == 5, "5 of the 7 lines have no return"
    assert r["unmatched_keys"][0] == (10001, "P1") and len(r["unmatched_keys"]) == 5, (
        "with several key columns, unmatched_keys holds sorted (order_id, product_id) tuples; got %s" % r["unmatched_keys"])
    assert out["refund"].notna().sum() == 2, "the two returned lines get their refund"


def test_inputs_unchanged(orders, customers):
    o, c = orders.copy(), customers.copy()
    safe_merge(orders, customers, on="customer_id")
    pd.testing.assert_frame_equal(orders, o, obj="left")
    pd.testing.assert_frame_equal(customers, c, obj="right")
