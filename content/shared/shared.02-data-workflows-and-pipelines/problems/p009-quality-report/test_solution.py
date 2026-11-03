import copy
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from solution import quality_report

UTC = timezone.utc
COLS = ["id", "amount", "updated_at", "city"]


def t(day, hour, minute=0, second=0):
    return datetime(2024, 6, day, hour, minute, second, tzinfo=UTC)


def example_rows():
    return [
        {"id": 1, "amount": Decimal("10.00"), "updated_at": t(1, 8), "city": "Pune"},
        {"id": 2, "amount": None, "updated_at": t(1, 9), "city": None},
        {"id": 2, "amount": Decimal("-5.00"), "updated_at": None, "city": "Goa"},
        {"id": 4, "amount": Decimal("250000"), "updated_at": t(1, 11)},
        {"id": 1, "amount": Decimal("0"), "updated_at": datetime(2024, 5, 31, 23, tzinfo=UTC), "city": "Pune"},
    ]


def test_example_from_the_statement():
    report = quality_report(example_rows(), COLS, now=t(2, 10))
    assert set(report) == {"rows", "null_rate", "duplicate_ids", "out_of_range", "newest", "fresh"}, (
        f"Keys were {sorted(report)}."
    )
    assert report["rows"] == 5
    assert report["null_rate"] == {"id": 0.0, "amount": 0.2, "updated_at": 0.2, "city": 0.4}, (
        f"null_rate was {report['null_rate']}. Row 4 has no 'city' key: count a missing key as None "
        "(use row.get(column))."
    )
    assert report["duplicate_ids"] == [1, 2], f"duplicate_ids was {report['duplicate_ids']}; ids 1 and 2 appear twice."
    assert report["out_of_range"] == [2, 4], (
        f"out_of_range was {report['out_of_range']}. -5.00 (id 2) and 250000 (id 4) are outside 0..100000; "
        "0 is inside (both ends allowed) and None is not checked."
    )
    assert report["newest"] == t(1, 11), "newest is the largest non-None updated_at."
    assert report["fresh"] is True, "The newest row is 23 hours old; max_age is 24 hours."


def test_null_rate_rounding():
    rows = [{"id": 1, "city": None}, {"id": 2, "city": "Pune"}, {"id": 3, "city": None}]
    report = quality_report(rows, ["id", "city", "amount"], now=t(2, 0))
    assert report["null_rate"] == {"id": 0.0, "city": 0.667, "amount": 1.0}, (
        f"null_rate was {report['null_rate']}. 2 of 3 is 0.667 after round(x, 3); "
        "'amount' is missing from every row, so its rate is 1.0."
    )


def test_null_rate_only_for_requested_columns_in_order():
    report = quality_report(example_rows(), ["city", "id"], now=t(2, 10))
    assert list(report["null_rate"]) == ["city", "id"], (
        f"null_rate keys were {list(report['null_rate'])}. Report exactly the given columns, in the given order."
    )


def test_zero_and_empty_string_are_not_null():
    rows = [{"id": 0, "amount": Decimal("0"), "city": ""}, {"id": 5, "amount": Decimal("1"), "city": "Goa"}]
    report = quality_report(rows, ["id", "amount", "city"], now=t(2, 0))
    assert report["null_rate"] == {"id": 0.0, "amount": 0.0, "city": 0.0}, (
        "0 and '' are values, not nulls. Test 'is None', not truthiness."
    )


def test_freshness_boundary():
    rows = [{"id": 1, "updated_at": t(1, 11)}]
    assert quality_report(rows, [], now=t(2, 11))["fresh"] is True, (
        "Exactly 24 hours old is still fresh: the rule is now - newest <= max_age."
    )
    assert quality_report(rows, [], now=t(2, 11, 0, 1))["fresh"] is False, (
        "24 hours and 1 second old is stale."
    )
    assert quality_report(rows, [], now=t(1, 13), max_age=timedelta(hours=1))["fresh"] is False, (
        "Use the max_age argument: 2 hours old with max_age=1 hour is stale."
    )


def test_freshness_uses_the_newest_row_not_the_last_one():
    rows = [{"id": 1, "updated_at": t(3, 9)}, {"id": 2, "updated_at": t(1, 9)}]
    report = quality_report(rows, [], now=t(3, 10))
    assert report["newest"] == t(3, 9), "newest is max(updated_at), not the last row's value."
    assert report["fresh"] is True


def test_no_timestamps():
    rows = [{"id": 1, "updated_at": None}, {"id": 2}]
    report = quality_report(rows, ["updated_at"], now=t(2, 0))
    assert report["newest"] is None and report["fresh"] is False, (
        "With no updated_at at all, newest is None and the batch is not fresh (max() of an empty list would crash)."
    )
    assert report["null_rate"] == {"updated_at": 1.0}


def test_empty_batch():
    report = quality_report([], COLS, now=t(2, 0))
    assert report == {"rows": 0, "null_rate": {"id": 0.0, "amount": 0.0, "updated_at": 0.0, "city": 0.0},
                      "duplicate_ids": [], "out_of_range": [], "newest": None, "fresh": False}, (
        f"Got {report}. An empty batch must not divide by zero: rates are 0.0."
    )


def test_duplicates_sorted_listed_once_and_none_ignored():
    rows = [{"id": 9}, {"id": 3}, {"id": 9}, {"id": 9}, {"id": None}, {"id": None}, {"id": 3}, {"id": 5}]
    report = quality_report(rows, ["id"], now=t(2, 0))
    assert report["duplicate_ids"] == [3, 9], (
        f"duplicate_ids was {report['duplicate_ids']}. Sorted, each id once (9 appears 3 times), "
        "and None ids are not duplicates (they are nulls)."
    )
    assert report["null_rate"] == {"id": 0.25}


def test_custom_amount_range():
    rows = [{"id": 1, "amount": Decimal("1")}, {"id": 2, "amount": Decimal("0.99")},
            {"id": 3, "amount": Decimal("100")}, {"id": 4, "amount": Decimal("100.01")}, {"id": 5}]
    report = quality_report(rows, [], now=t(2, 0), amount_range=(Decimal("1"), Decimal("100")))
    assert report["out_of_range"] == [2, 4], (
        f"out_of_range was {report['out_of_range']}. Use the amount_range argument; 1 and 100 are inside "
        "(both ends allowed); a missing amount is not out of range."
    )


def test_rows_not_changed():
    rows = example_rows()
    before = copy.deepcopy(rows)
    quality_report(rows, COLS, now=t(2, 10))
    assert rows == before, "A report must only read the rows (do not fill in missing keys)."
