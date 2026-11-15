import sqlite3

import pytest

from solution import TooManyBadRecords, load_with_threshold


def good(i, status="shipped", amount="10.00"):
    return {"id": i, "customer": {"email": f"u{i}@example.com", "city": None},
            "status": status, "amount": amount, "currency": "INR"}


def table(conn):
    return conn.execute("SELECT id, status, amount FROM orders ORDER BY id").fetchall()


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, status TEXT NOT NULL, amount TEXT NOT NULL)")
    return conn


def test_all_good():
    conn = fresh()
    summary = load_with_threshold(conn, [good(i) for i in range(1, 6)])
    assert summary == {"total": 5, "loaded": 5, "bad": 0, "errors": {}, "failures": []}, (
        f"Summary {summary}. With no bad records: total 5, loaded 5, bad 0, empty errors/failures."
    )
    assert [row[0] for row in table(conn)] == [1, 2, 3, 4, 5]


def test_one_bad_in_ten_is_exactly_the_limit():
    conn = fresh()
    records = [good(i) for i in range(1, 10)] + [good(10, status="lost")]
    summary = load_with_threshold(conn, records, max_bad_ratio=0.1)
    assert summary["loaded"] == 9 and summary["bad"] == 1, (
        "1 of 10 is exactly 10 %: NOT more than max_bad_ratio=0.1, so load the 9 good ones. "
        "Use '>' (strictly greater), not '>='."
    )
    assert summary["failures"] == [(9, "bad status")], (
        f"failures {summary['failures']}; give the 0-based index of the record and its reason."
    )
    assert summary["errors"] == {"bad status": 1}
    assert len(table(conn)) == 9


def test_two_bad_in_ten_aborts_and_writes_nothing():
    conn = fresh()
    records = [good(i) for i in range(1, 9)] + [None, "oops"]
    with pytest.raises(TooManyBadRecords) as info:
        load_with_threshold(conn, records, max_bad_ratio=0.1)
    assert table(conn) == [], (
        "The batch was aborted but some rows were written. Validate ALL records first, decide, "
        "and only then write (or roll back)."
    )
    assert "2 of 10" in str(info.value), f"Message {str(info.value)!r} must say '2 of 10 records are bad ...'."
    s = info.value.summary
    assert (s["total"], s["loaded"], s["bad"]) == (10, 0, 2), (
        f"The exception's summary has total/loaded/bad = {(s['total'], s['loaded'], s['bad'])}; "
        "expected (10, 0, 2): nothing was loaded."
    )
    assert s["failures"] == [(8, "not an object"), (9, "not an object")]


def test_abort_leaves_existing_rows_untouched():
    conn = fresh()
    load_with_threshold(conn, [good(1), good(2)])
    before = table(conn)
    batch = [good(1, status="cancelled"), good(3), {"id": 4}, {"id": 5, "status": "x"}]
    with pytest.raises(TooManyBadRecords):
        load_with_threshold(conn, batch, max_bad_ratio=0.25)
    assert table(conn) == before, (
        "An aborted batch must not update order 1 or insert order 3. The table must be exactly "
        "as before the call."
    )


def test_every_reason():
    conn = fresh()
    records = [
        good(1),
        None,                                       # 1 not an object
        ["id", 2],                                  # 2 not an object
        {"status": "shipped", "amount": "1.00"},    # 3 bad id (missing)
        good(True),                                 # 4 bad id (bool)
        good(-4),                                   # 5 bad id
        good("6"),                                  # 6 bad id (string)
        good(7, status="SHIPPED"),                  # 7 bad status (case matters)
        {"id": 8, "amount": "1.00"},                # 8 bad status (missing)
        good(9, amount=9.5),                        # 9 bad amount (float, not str)
        good(10, amount="ten"),                     # 10 bad amount
        good(11, amount="-0.01"),                   # 11 bad amount
        {"id": 12, "status": "pending"},            # 12 bad amount (missing)
        good(1, status="pending"),                  # 13 duplicate id (1 was accepted)
        good(14, status="pending", amount="0"),     # ok
    ]
    summary = load_with_threshold(conn, records, max_bad_ratio=1.0)
    expected = [(1, "not an object"), (2, "not an object"), (3, "bad id"), (4, "bad id"),
                (5, "bad id"), (6, "bad id"), (7, "bad status"), (8, "bad status"),
                (9, "bad amount"), (10, "bad amount"), (11, "bad amount"), (12, "bad amount"),
                (13, "duplicate id")]
    for got, want in zip(summary["failures"], expected):
        assert got == want, (
            f"Record {want[0]} ({records[want[0]]!r}) should fail with {want[1]!r}, got {got}. "
            "Check in the order: object, id, status, amount, duplicate."
        )
    assert summary["failures"] == expected
    assert summary["errors"] == {"not an object": 2, "bad id": 4, "bad status": 2,
                                 "bad amount": 4, "duplicate id": 1}
    assert table(conn) == [(1, "shipped", "10.00"), (14, "pending", "0")], (
        "Only records 0 and 14 are valid. The duplicate must not overwrite the first order 1."
    )


def test_duplicate_of_a_rejected_record_is_not_a_duplicate():
    conn = fresh()
    summary = load_with_threshold(conn, [good(5, status="lost"), good(5)], max_bad_ratio=0.5)
    assert summary["failures"] == [(0, "bad status")], (
        "The first id 5 was rejected, so the second id 5 is the first ACCEPTED one, not a duplicate."
    )
    assert table(conn) == [(5, "shipped", "10.00")]


def test_existing_ids_are_updated():
    conn = fresh()
    load_with_threshold(conn, [good(1), good(2)])
    summary = load_with_threshold(conn, [good(2, status="cancelled", amount="0.00"), good(3)])
    assert summary["loaded"] == 2
    assert table(conn) == [(1, "shipped", "10.00"), (2, "cancelled", "0.00"), (3, "shipped", "10.00")], (
        "An id from an EARLIER batch is not a duplicate; upsert it (ON CONFLICT DO UPDATE)."
    )


def test_empty_batch():
    conn = fresh()
    assert load_with_threshold(conn, []) == {"total": 0, "loaded": 0, "bad": 0, "errors": {}, "failures": []}, (
        "An empty batch loads nothing and must not divide by zero."
    )


def test_zero_tolerance():
    conn = fresh()
    assert load_with_threshold(conn, [good(1), good(2)], max_bad_ratio=0)["loaded"] == 2
    with pytest.raises(TooManyBadRecords):
        load_with_threshold(conn, [good(3)] * 1 + [good(4, amount="x")] + [good(i) for i in range(5, 105)],
                            max_bad_ratio=0)
    assert [row[0] for row in table(conn)] == [1, 2], "With max_bad_ratio=0 a single bad record aborts."


def test_creates_the_table_and_commits(tmp_path):
    path = tmp_path / "o.db"
    conn = sqlite3.connect(path)
    load_with_threshold(conn, [good(1)])
    other = sqlite3.connect(path)
    rows = other.execute("SELECT id FROM orders").fetchall()
    other.close()
    conn.close()
    assert rows == [(1,)], (
        "Create the table if needed (CREATE TABLE IF NOT EXISTS) and commit, so other "
        "connections see the rows."
    )


def test_large_batch_threshold():
    conn = fresh()
    records = [good(i) for i in range(1, 1001)]
    for i in range(0, 1000, 20):                  # 50 bad of 1000 = 5 %
        records[i] = good(records[i]["id"], amount="n/a")
    summary = load_with_threshold(conn, records, max_bad_ratio=0.05)
    assert (summary["bad"], summary["loaded"]) == (50, 950)
    records[1] = None                              # 51 of 1000 = 5.1 %
    with pytest.raises(TooManyBadRecords):
        load_with_threshold(conn, records, max_bad_ratio=0.05)
