from decimal import Decimal

import pytest
from django.db import IntegrityError, connection
from django.test.utils import CaptureQueriesContext

from solution import Item, import_items

ROWS = [
    {"sku": "A1", "name": "Pen", "price": "1.50"},
    {"sku": "B2", "name": "Ink", "price": "4.00"},
]


def snapshot():
    return list(Item.objects.order_by("sku").values_list("sku", "name", "price", "quantity"))


def test_first_run_creates_everything():
    result = import_items(ROWS)
    assert tuple(result) == (2, 0), f"Two new skus must give (2, 0), got {result!r}."
    assert snapshot() == [("A1", "Pen", Decimal("1.50"), 0), ("B2", "Ink", Decimal("4.00"), 0)], (
        f"New items need sku, name, price and quantity 0, got {snapshot()}.")


def test_second_run_changes_nothing():
    import_items(ROWS)
    before = snapshot()
    result = import_items(ROWS)
    assert tuple(result) == (0, 2), f"Running the same rows again must give (0, 2), got {result!r}."
    assert snapshot() == before, "The database must be identical after the second run (idempotence)."
    assert Item.objects.count() == 2, "A second run must not create duplicates."


def test_existing_item_gets_new_name_and_price_but_keeps_its_quantity():
    Item.objects.create(sku="A1", name="Old", price="9.99", quantity=42)
    result = import_items([{"sku": "A1", "name": "Pen", "price": "1.50"}])
    assert tuple(result) == (0, 1), f"One existing sku must give (0, 1), got {result!r}."
    item = Item.objects.get(sku="A1")
    assert (item.name, item.price) == ("Pen", Decimal("1.50")), "name and price must be updated from the row."
    assert item.quantity == 42, "quantity belongs to stock-keeping: the import must not reset it to 0."


def test_mixed_new_and_existing():
    Item.objects.create(sku="A1", name="Old", price="9.99", quantity=3)
    result = import_items(ROWS + [{"sku": "C3", "name": "Cap", "price": "0.50"}])
    assert tuple(result) == (2, 1), f"Expected 2 created (B2, C3) and 1 updated (A1), got {result!r}."
    assert Item.objects.count() == 3


def test_empty_import():
    assert tuple(import_items([])) == (0, 0), "No rows: (0, 0)."


def test_the_same_sku_twice_last_row_wins_and_counts_once():
    rows = [{"sku": "A1", "name": "First", "price": "1.00"}, {"sku": "A1", "name": "Second", "price": "2.00"}]
    result = import_items(rows)
    assert tuple(result) == (1, 0), f"A repeated sku counts once, got {result!r}."
    item = Item.objects.get(sku="A1")
    assert (item.name, item.price) == ("Second", Decimal("2.00")), "The last row of a sku must win."


def test_a_big_new_batch_is_not_one_query_per_row():
    rows = [{"sku": f"S{i}", "name": f"Item {i}", "price": "1.00"} for i in range(300)]
    with CaptureQueriesContext(connection) as ctx:
        result = import_items(rows)
    assert tuple(result) == (300, 0), f"300 new rows must give (300, 0), got {result!r}."
    assert Item.objects.count() == 300
    assert len(ctx) <= 12, (
        f"300 new rows used {len(ctx)} queries (limit 12). Do not call update_or_create in a loop for new rows: "
        "find the existing skus with ONE query and use bulk_create for the rest.")


def test_second_run_of_a_big_batch_is_still_correct():
    rows = [{"sku": f"S{i}", "name": f"Item {i}", "price": "1.00"} for i in range(300)]
    import_items(rows)
    assert tuple(import_items(rows)) == (0, 300), "The second run must report 0 created and 300 updated."
    assert Item.objects.count() == 300, "No duplicates after the second run."


def test_a_bad_new_row_rolls_back_the_updates():
    Item.objects.create(sku="A1", name="Old", price="9.99")
    rows = [{"sku": "A1", "name": "Pen", "price": "1.50"}, {"sku": "Z9", "name": "Bad", "price": None}]
    with pytest.raises(IntegrityError):
        import_items(rows)
    assert snapshot() == [("A1", "Old", Decimal("9.99"), 0)], (
        "When one row fails, nothing of this call may stay: wrap the whole import in transaction.atomic().")


def test_a_bad_update_row_rolls_back_the_creates():
    Item.objects.create(sku="A1", name="Old", price="9.99")
    rows = [{"sku": "N1", "name": "New", "price": "1.00"}, {"sku": "A1", "name": "Pen", "price": None}]
    with pytest.raises(IntegrityError):
        import_items(rows)
    assert Item.objects.filter(sku="N1").count() == 0, (
        "The new item N1 must not stay when another row fails: use one transaction.atomic() around everything.")
