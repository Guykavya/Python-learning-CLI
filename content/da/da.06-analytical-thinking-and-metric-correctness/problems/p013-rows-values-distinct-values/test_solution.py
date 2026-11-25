import pandas as pd

from solution import three_counts


def payments():
    return pd.DataFrame({
        "payment_id":  [1, 2, 3, 4, 5, 6, 7, 8],
        "customer_id": [1, 1, 2, 3, 3, 3, 4, 5],       # customers 1 and 3 pay several times: 5 different customers
        "method": ["card", "upi", None, "card", "upi", "upi", None, "card"],   # two payments with no method recorded
    })


def test_rows():
    got = three_counts(payments())["rows"]
    assert got == 8, "'rows' is the number of payments: every row counts, even one with a missing method. Got %s." % got


def test_with_method():
    got = three_counts(payments())["with_method"]
    assert got == 6, "'with_method' skips the 2 rows where the method is missing: use count() on the method column. Got %s." % got


def test_distinct_customers():
    got = three_counts(payments())["distinct_customers"]
    assert got == 5, "'distinct_customers' counts each paying customer once (1, 2, 3, 4, 5): use nunique(), not len(). Got %s." % got


def test_the_three_counts_differ():
    got = three_counts(payments())
    assert len({got["rows"], got["with_method"], got["distinct_customers"]}) == 3, (
        "the three numbers answer three different questions and must all differ here: %s." % got)


def test_plain_ints_and_exactly_three_keys():
    got = three_counts(payments())
    assert sorted(got) == ["distinct_customers", "rows", "with_method"], "the dict has exactly the keys rows, with_method, distinct_customers."
    assert all(type(v) is int for v in got.values()), "return plain ints: wrap in int(...)."


def test_empty_table():
    empty = pd.DataFrame({"payment_id": [], "customer_id": [], "method": []})
    assert three_counts(empty) == {"rows": 0, "with_method": 0, "distinct_customers": 0}, "an empty table has 0 of everything."


def test_missing_customer_is_not_a_customer():
    df = pd.DataFrame({"customer_id": [1, None, None], "method": ["card", "card", "card"]})
    assert three_counts(df)["distinct_customers"] == 1, "nunique() skips missing values: two payments of unknown customers are not a customer."


def test_frame_is_not_changed():
    p = payments()
    before = p.copy()
    three_counts(p)
    pd.testing.assert_frame_equal(p, before)
