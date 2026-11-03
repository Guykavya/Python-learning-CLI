import copy
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from solution import flatten_order

UTC = timezone.utc
KEYS = {"id", "email", "city", "status", "amount", "currency", "created_at", "updated_at",
        "item_count", "total_qty"}


def make(**changes):
    order = {"id": 101, "customer": {"email": "asha@example.com", "city": "Pune"}, "status": "shipped",
             "amount": "19.99", "currency": "INR", "created_at": "2024-06-01T10:00:00Z",
             "updated_at": "2024-06-01T12:00:00Z", "items": [{"sku": "B1", "qty": 2}]}
    customer = changes.pop("customer", {})
    order["customer"].update(customer)
    order.update(changes)
    return order


def test_default_order():
    row = flatten_order(make())
    assert set(row) == KEYS, f"Keys were {sorted(row)}; expected exactly {sorted(KEYS)}."
    assert row == {"id": 101, "email": "asha@example.com", "city": "Pune", "status": "shipped",
                   "amount": Decimal("19.99"), "currency": "INR",
                   "created_at": datetime(2024, 6, 1, 10, 0, tzinfo=UTC),
                   "updated_at": datetime(2024, 6, 1, 12, 0, tzinfo=UTC),
                   "item_count": 1, "total_qty": 2}, f"Row was {row}."


def test_amount_is_decimal_not_float():
    row = flatten_order(make(amount="0.10"))
    assert type(row["amount"]) is Decimal, (
        f"amount is a {type(row['amount']).__name__}. Use Decimal(text): float(\"0.10\") cannot "
        "hold 0.10 exactly, and money sums drift."
    )
    total = flatten_order(make(amount="0.10"))["amount"] + flatten_order(make(amount="0.20"))["amount"]
    assert total == Decimal("0.30"), f"0.10 + 0.20 gave {total}; with Decimal it is exactly 0.30."
    assert str(flatten_order(make(amount="5.00"))["amount"]) == "5.00", (
        "Decimal('5.00') keeps its two decimal places. Did you go through float or int?"
    )


def test_offset_is_converted_to_utc():
    row = flatten_order(make(created_at="2024-06-01T15:30:00+05:30"))
    assert row["created_at"] == datetime(2024, 6, 1, 10, 0, tzinfo=UTC)
    assert row["created_at"].utcoffset() == timedelta(0), (
        f"created_at has offset {row['created_at'].utcoffset()}. Convert with .astimezone(timezone.utc) "
        "so every row in the table uses the same zone."
    )
    assert row["created_at"].hour == 10, "15:30 at +05:30 is 10:00 UTC."


def test_negative_offset_crosses_midnight():
    row = flatten_order(make(updated_at="2024-06-01T21:00:00-04:00"))
    assert row["updated_at"] == datetime(2024, 6, 2, 1, 0, tzinfo=UTC), (
        f"Got {row['updated_at']}. 21:00 at -04:00 is 01:00 UTC on the NEXT day."
    )
    assert row["updated_at"].tzinfo is not None


def test_naive_timestamp_raises_value_error_naming_the_field():
    with pytest.raises(ValueError) as info:
        flatten_order(make(updated_at="2024-06-01T12:00:00"))
    assert "updated_at" in str(info.value), (
        f"Message {str(info.value)!r} must name the field. A timestamp with no offset is ambiguous; "
        "raise ValueError instead of guessing UTC or local time."
    )
    with pytest.raises(ValueError):
        flatten_order(make(created_at="2024-06-01 08:00:00"))


def test_strings_are_normalised():
    row = flatten_order(make(customer={"email": "  Ravi.K@Example.COM ", "city": "  new delhi "},
                             status=" Pending ", currency=" inr"))
    assert row["email"] == "ravi.k@example.com", f"email was {row['email']!r}; strip() and lower()."
    assert row["city"] == "New Delhi", f"city was {row['city']!r}; strip() and title()."
    assert row["status"] == "pending", f"status was {row['status']!r}; strip() and lower()."
    assert row["currency"] == "INR", f"currency was {row['currency']!r}; strip() and upper()."


def test_null_city_stays_none():
    row = flatten_order(make(customer={"city": None}))
    assert row["city"] is None, "city null must become None, not the string 'None' (and must not crash)."


def test_blank_city_becomes_none():
    row = flatten_order(make(customer={"city": "   "}))
    assert row["city"] is None, (
        f"city was {row['city']!r}. A blank city carries no information; store None so null checks find it."
    )


def test_items_counted_and_summed():
    row = flatten_order(make(items=[{"sku": "B1", "qty": 2}, {"sku": "C7", "qty": 1}, {"sku": "D3", "qty": 4}]))
    assert row["item_count"] == 3, f"item_count was {row['item_count']}; it is the number of item lines."
    assert row["total_qty"] == 7, f"total_qty was {row['total_qty']}; it is 2 + 1 + 4."


def test_no_items():
    row = flatten_order(make(items=[]))
    assert (row["item_count"], row["total_qty"]) == (0, 0), "An order with no items has count 0 and qty 0."


def test_input_is_not_changed():
    order = make(customer={"email": " X@Example.com "}, created_at="2024-06-01T15:30:00+05:30")
    before = copy.deepcopy(order)
    flatten_order(order)
    assert order == before, "flatten_order changed its input. Build a new dict; keep the raw record as it was."


def test_different_order():
    order = {"id": 7, "customer": {"email": "meera@example.com", "city": "kochi"}, "status": "cancelled",
             "amount": "1250.50", "currency": "usd", "created_at": "2023-12-31T23:59:59+00:00",
             "updated_at": "2024-01-01T05:29:59+05:30", "items": [{"sku": "Z", "qty": 10}]}
    row = flatten_order(order)
    assert row["id"] == 7 and row["city"] == "Kochi" and row["amount"] == Decimal("1250.50")
    assert row["created_at"] == row["updated_at"] == datetime(2023, 12, 31, 23, 59, 59, tzinfo=UTC), (
        "Both timestamps are the same moment (05:29:59 at +05:30 is 23:59:59 UTC the day before)."
    )
    assert (row["item_count"], row["total_qty"]) == (1, 10)
