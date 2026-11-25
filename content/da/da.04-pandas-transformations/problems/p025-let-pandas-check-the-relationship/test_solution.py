import pandas as pd
import pytest

from solution import lookup_products


def lines():
    return pd.DataFrame({
        "order_id": [1, 1, 2, 3, 3, 3, 4],
        "product_id": ["P003", "P001", "P002", "P005", "P001", "P008", "P002"],
        "qty": [1, 2, 1, 4, 1, 1, 2],
        "unit_price": [30.0, 10.0, 20.0, 5.0, 10.0, 8.0, 18.0],
    })


def products():
    return pd.DataFrame({
        "product_id": ["P001", "P002", "P003", "P004", "P005"],
        "category": ["home", "toys", "home", "office", "beauty"],
        "list_price": [10.0, 20.0, 30.0, 40.0, 5.0],
    })


def test_every_line_once():
    out = lookup_products(lines(), products())
    assert len(out) == len(lines()), "one row per line: a many-to-one left join keeps the row count (%d)." % len(lines())
    assert out["order_id"].tolist() == [1, 1, 2, 3, 3, 3, 4], "lines in the original order."
    assert out.index.tolist() == list(range(7)), "index 0..n-1."
    assert list(out.columns) == ["order_id", "product_id", "qty", "unit_price", "category", "list_price"], (
        "columns: the line columns, then category and list_price. Got %s." % list(out.columns))


def test_values_attached_and_unknown_kept():
    out = lookup_products(lines(), products())
    assert out["category"].tolist()[:4] == ["home", "home", "toys", "beauty"], "each line gets its product's category."
    assert pd.isna(out["category"].tolist()[5]), "P008 is unknown: keep the line with a missing category."


def bad_products():
    p = products()
    return pd.concat([p, p.iloc[[4, 1, 4]]], ignore_index=True)       # P005 twice extra, P002 once extra


def test_duplicates_raise_valueerror():
    with pytest.raises(ValueError):
        lookup_products(lines(), bad_products())


def test_message_lists_the_duplicated_ids():
    try:
        lookup_products(lines(), bad_products())
    except ValueError as e:
        msg = str(e)
    else:
        pytest.fail("a duplicated product_id must raise: use validate='m:1'. Without it the merge silently "
                    "duplicates lines (fan-out).")
    assert "P002" in msg and "P005" in msg, (
        "the message must name every duplicated id (P002 and P005), so the data owner knows what to fix. "
        "pandas' own MergeError does not; catch it and raise ValueError with the ids. Got: %r" % msg)
    assert "P001" not in msg and "P003" not in msg, "list only the DUPLICATED ids, not all ids. Got: %r" % msg
    assert msg.count("P005") == 1, "each duplicated id once, even if it appears three times. Got: %r" % msg


def test_duplicate_of_unused_product_still_raises():
    p = pd.concat([products(), products().iloc[[3]]], ignore_index=True)       # P004 duplicated, never sold
    with pytest.raises(ValueError) as info:
        lookup_products(lines(), p)
    assert "P004" in str(info.value), "validate checks the whole product table, even ids no line uses."


def test_inputs_not_changed():
    l, p = lines(), bad_products()
    lb, pb = l.copy(), p.copy()
    try:
        lookup_products(l, p)
    except ValueError:
        pass
    pd.testing.assert_frame_equal(l, lb, obj="the input lines")
    pd.testing.assert_frame_equal(p, pb, obj="the input products")
