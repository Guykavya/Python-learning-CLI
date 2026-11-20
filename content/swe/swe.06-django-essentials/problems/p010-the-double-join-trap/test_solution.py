import pytest
from django.db import connection
from django.db.models import QuerySet
from django.test.utils import CaptureQueriesContext

from solution import Category, Item, Movement, Supplier, item_stats

# name, number of suppliers, number of movements
PLAN = [
    ("Cable", 2, 3),    # naive answer: 6 and 6
    ("Dock", 3, 2),     # naive answer: 6 and 6
    ("Hub", 1, 0),
    ("Mouse", 0, 2),
    ("Pad", 0, 0),
    ("Stand", 4, 5),    # naive answer: 20 and 20
]


@pytest.fixture(autouse=True)
def data():
    category = Category.objects.create(name="Misc")
    suppliers = [Supplier.objects.create(name=f"Supplier {n}") for n in range(4)]
    for number, (name, n_suppliers, n_movements) in enumerate(PLAN):
        item = Item.objects.create(name=name, sku=f"S{number}", price="1.00", category=category)
        item.suppliers.add(*suppliers[:n_suppliers])
        for k in range(n_movements):
            Movement.objects.create(item=item, delta=k + 1, reason="seed")


def stats():
    return {i.name: (i.supplier_count, i.movement_count) for i in item_stats()}


def test_counts_are_correct_for_every_item():
    expected = {name: (s, m) for name, s, m in PLAN}
    assert stats() == expected, (
        f"Wrong counts: got {stats()}, expected {expected}. "
        "Counting two relations in one annotate() multiplies the joined rows (2 suppliers x 3 movements = 6). "
        "Use Count('...', distinct=True) or a Subquery for each number.")


def test_the_naive_double_count_would_be_wrong():
    # a guard that the data really contains the trap
    naive = Item.objects.get(name="Cable")
    assert (naive.suppliers.count(), naive.movements.count()) == (2, 3)


def test_items_without_suppliers_or_movements_count_zero():
    result = stats()
    assert result["Pad"] == (0, 0), f"An item with no suppliers and no movements must show (0, 0), got {result['Pad']}."
    assert result["Mouse"] == (0, 2), f"Mouse has no suppliers but 2 movements: expected (0, 2), got {result['Mouse']}."
    assert result["Hub"] == (1, 0), f"Hub has 1 supplier and no movements: expected (1, 0), got {result['Hub']}."


def test_every_item_is_listed_once():
    names = [i.name for i in item_stats()]
    assert names == sorted(n for n, _, _ in PLAN), f"Each item must appear exactly once, in name order. Got {names}."


def test_one_query():
    with CaptureQueriesContext(connection) as ctx:
        for item in item_stats():
            _ = item.supplier_count, item.movement_count
    assert len(ctx) == 1, f"Reading all the counts took {len(ctx)} queries; it must be 1 (do the counting in the database)."


def test_returns_item_objects_in_a_queryset():
    result = item_stats()
    assert isinstance(result, QuerySet), f"item_stats() must return a QuerySet, got {type(result).__name__}."
    assert all(isinstance(i, Item) for i in result), "The result must contain Item objects, not dictionaries."


def test_annotations_can_be_filtered():
    many = item_stats().filter(supplier_count__gte=3)
    assert sorted(i.name for i in many) == ["Dock", "Stand"], "supplier_count must be usable in filter(supplier_count__gte=3)."
