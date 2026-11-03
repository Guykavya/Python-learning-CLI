import copy

from solution import dedupe_latest


def rec(id_, updated_at, status="shipped"):
    return {"id": id_, "status": status, "updated_at": updated_at}


def test_example_from_the_statement():
    records = [
        rec(101, "2024-06-01T10:00:00Z", "pending"),
        rec(102, "2024-06-01T10:05:00Z", "pending"),
        rec(101, "2024-06-01T12:00:00Z", "shipped"),
        rec(102, "2024-06-01T09:00:00Z", "cancelled"),
    ]
    got = dedupe_latest(records)
    assert [r["id"] for r in got] == [101, 102], (
        f"Got ids {[r['id'] for r in got]}. Return one record per id, ids in first-seen order."
    )
    assert got[0]["status"] == "shipped", "For 101 the 12:00 version is the newest; keep it."
    assert got[1]["status"] == "pending", (
        "For 102 the second version (09:00) is OLDER than the first (10:05). Keep the newest, "
        "not simply the last one in the list."
    )


def test_no_duplicates_returns_everything_in_order():
    records = [rec(5, "2024-01-01T00:00:00Z"), rec(3, "2024-01-02T00:00:00Z"), rec(9, "2024-01-03T00:00:00Z")]
    got = dedupe_latest(records)
    assert [r["id"] for r in got] == [5, 3, 9], (
        "Without duplicates every record stays, in input order. Do not sort by id or by time."
    )


def test_empty_input():
    assert dedupe_latest([]) == [], "No records in, no records out."


def test_compares_instants_not_strings():
    records = [
        rec(7, "2024-06-01T09:00:00+05:30", "pending"),   # 03:30 UTC
        rec(7, "2024-06-01T04:00:00Z", "shipped"),        # 04:00 UTC: really the newest
    ]
    got = dedupe_latest(records)
    assert len(got) == 1 and got[0]["status"] == "shipped", (
        "09:00+05:30 is 03:30 UTC, earlier than 04:00Z. Comparing the strings picks the wrong "
        "one: parse with datetime.fromisoformat and compare datetimes."
    )
    records.reverse()
    got = dedupe_latest(records)
    assert got[0]["status"] == "shipped", (
        "Same data in the other order: the 04:00Z version must still win, it is the later instant."
    )


def test_tie_keeps_the_last_seen():
    records = [
        rec(1, "2024-06-01T10:00:00Z", "pending"),
        rec(1, "2024-06-01T10:00:00Z", "shipped"),
    ]
    assert dedupe_latest(records)[0]["status"] == "shipped", (
        "Equal updated_at: keep the record that comes LATER in the input. Use >= when you "
        "compare, not >."
    )


def test_tie_written_with_different_offsets():
    records = [
        rec(1, "2024-06-01T15:30:00+05:30", "pending"),   # 10:00 UTC
        rec(1, "2024-06-01T10:00:00Z", "cancelled"),      # 10:00 UTC, same instant
    ]
    assert dedupe_latest(records)[0]["status"] == "cancelled", (
        "15:30+05:30 and 10:00Z are the same instant, so it is a tie and the last seen wins."
    )


def test_newer_then_older_then_tie():
    records = [
        rec(4, "2024-06-03T08:00:00Z", "a"),
        rec(8, "2024-06-01T00:00:00Z", "x"),
        rec(4, "2024-06-02T08:00:00Z", "b"),   # older than a
        rec(4, "2024-06-03T08:00:00Z", "c"),   # ties with a, seen later
        rec(8, "2024-06-01T00:00:01Z", "y"),   # one second newer
        rec(4, "2024-06-01T08:00:00Z", "d"),   # older again
    ]
    got = dedupe_latest(records)
    assert [(r["id"], r["status"]) for r in got] == [(4, "c"), (8, "y")], (
        f"Got {[(r['id'], r['status']) for r in got]}. For id 4: 'c' ties with 'a' and comes "
        "later, 'b' and 'd' are older. For id 8: 'y' is one second newer. Ids stay in "
        "first-seen order (4 before 8)."
    )


def test_returns_the_same_dicts_and_leaves_input_alone():
    records = [rec(1, "2024-06-01T10:00:00Z"), rec(2, "2024-06-01T10:00:00Z"), rec(1, "2024-06-01T11:00:00Z")]
    before = copy.deepcopy(records)
    got = dedupe_latest(records)
    assert records == before, "Do not change the input list or the records in it."
    assert got[0] is records[2] and got[1] is records[1], (
        "Return the original record dicts (the winners), not new or modified ones."
    )


def test_many_versions():
    records = []
    for version in range(50):
        for id_ in (30, 10, 20):
            hour = (version * 7 + id_) % 24
            records.append(rec(id_, f"2024-06-{1 + version % 5:02d}T{hour:02d}:00:00Z", f"v{version}"))
    got = dedupe_latest(records)
    assert [r["id"] for r in got] == [30, 10, 20], "Ids must keep first-seen order: 30, 10, 20."
    for r in got:
        same = [x for x in records if x["id"] == r["id"]]
        latest = max(x["updated_at"] for x in same)   # all 'Z' here, so strings are safe in the test
        last_with_latest = [x for x in same if x["updated_at"] == latest][-1]
        assert r is last_with_latest, (
            f"id {r['id']}: expected version {last_with_latest['status']}, got {r['status']}."
        )
