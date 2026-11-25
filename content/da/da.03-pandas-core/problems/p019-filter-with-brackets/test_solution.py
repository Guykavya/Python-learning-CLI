import pandas as pd
import pytest

from solution import big_orders


def frame():
    return pd.DataFrame({
        "city": ["Pune", "Pune", "Agra", "Agra", "Pune", "Delhi", "Pune"],
        "amount": [500, 100, 90, 800, 400, 700, 900],
        "status": ["paid", "paid", "paid", "cancelled", "paid", "paid", "cancelled"],
        "rush": [False, False, True, True, False, False, False],
    }, index=[10, 11, 12, 13, 14, 15, 16])


def slow(df, city, min_amount):
    keep = []
    for label, row in zip(df.index, df.itertuples(index=False)):
        ok = row.status != "cancelled" and ((row.city == city and row.amount >= min_amount) or bool(row.rush))
        if ok:
            keep.append(label)
    return keep


def call(df, city, amount):
    try:
        return big_orders(df, city, amount)
    except (ValueError, TypeError) as exc:
        pytest.fail("%s. Put each comparison in its own parentheses: (df['a'] > 1) & (df['b'] < 2); & binds tighter than >." % exc)


def test_example_rows():
    out = call(frame(), "Pune", 400)
    assert out.index.tolist() == [10, 12, 14], "expected labels [10, 12, 14] (big Pune orders and the rush order); got %s." % out.index.tolist()


def test_cancelled_rush_order_is_excluded():
    out = call(frame(), "Agra", 50)
    assert 13 not in out.index.tolist(), "row 13 is a cancelled rush order: ~(status == 'cancelled') applies to the whole condition, so parenthesise the (A | B) part."
    assert out.index.tolist() == [12], "Agra rows: 12 (paid) only; got %s." % out.index.tolist()


def test_boundary_is_inclusive():
    out = call(frame(), "Pune", 500)
    assert 10 in out.index.tolist() and 14 not in out.index.tolist(), "amount >= min_amount: 500 counts, 400 does not."


def test_matches_a_plain_loop_for_several_inputs():
    df = frame()
    for city in ["Pune", "Agra", "Delhi", "Nowhere"]:
        for amount in [0, 100, 400, 800, 1000]:
            assert call(df, city, amount).index.tolist() == slow(df, city, amount), "city=%s min=%s differs from the loop version." % (city, amount)


def test_keeps_all_columns_and_input_unchanged():
    df = frame()
    before = df.copy()
    out = call(df, "Pune", 400)
    assert out.columns.tolist() == ["city", "amount", "status", "rush"]
    pd.testing.assert_frame_equal(df, before, obj="the input frame")


def test_rush_row_survives_from_another_city():
    out = call(frame(), "Nowhere", 10 ** 6)
    assert out.index.tolist() == [12], "only the rush row 12 survives: rush orders are wanted from any city."
