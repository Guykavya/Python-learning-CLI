from decimal import Decimal

import pytest
from django.db import connection
from django.db.models import QuerySet
from django.test.utils import CaptureQueriesContext

from solution import Category, Item, category_values


@pytest.fixture(autouse=True)
def data():
    cables = Category.objects.create(name="Cables")
    computers = Category.objects.create(name="Computers")
    Category.objects.create(name="Spare")           # no items at all
    Category.objects.create(name="Archive")         # no items at all
    zero = Category.objects.create(name="Zero stock")
    rows = [
        ("USB cable", "CB-1", 120, "3.50", cables),
        ("Cable tie", "CB-2", 10, "1.25", cables),
        ("Keyboard", "KB-1", 10, "49.90", computers),
        ("Monitor", "MN-1", 3, "189.00", computers),
        ("Empty box", "ZB-1", 0, "5.00", zero),
    ]
    for name, sku, quantity, price, category in rows:
        Item.objects.create(name=name, sku=sku, quantity=quantity, price=price, category=category)
    Item.objects.filter(sku="MN-1").update(status="discontinued")   # still counts


def rows():
    return [(c.name, c.value) for c in category_values()]


def test_values_and_order():
    assert rows() == [
        ("Computers", Decimal("1066.00")),
        ("Cables", Decimal("432.50")),
        ("Archive", Decimal("0")),
        ("Spare", Decimal("0")),
        ("Zero stock", Decimal("0")),
    ], (f"Expected the categories by value descending (ties by name) with values 1066.00, 432.50, 0, 0, 0. Got {rows()}. "
        "Value = Sum(quantity * price) of the items; every status counts.")


def test_categories_without_items_have_zero_not_none():
    values = dict(rows())
    assert values["Spare"] is not None and values["Archive"] is not None, (
        "A category without items got value None (Sum of nothing is NULL). Wrap the Sum in Coalesce(..., 0).")
    assert values["Spare"] == 0, f"A category without items must have value 0, got {values['Spare']!r}."


def test_every_category_is_listed():
    assert len(category_values()) == 5, "All 5 categories must be in the result, including the ones without items."


def test_value_is_a_decimal():
    for category in category_values():
        assert isinstance(category.value, Decimal), (
            f"{category.name}: value should be a Decimal, got {type(category.value).__name__}. "
            "Give Coalesce an output_field=DecimalField(...) so that the 0 and the sum share one type.")


def test_zero_quantity_item_adds_nothing():
    assert dict(rows())["Zero stock"] == 0, "An item with quantity 0 contributes 0, even though it has a price."


def test_returns_a_queryset_and_costs_one_query():
    result = category_values()
    assert isinstance(result, QuerySet), f"category_values() must return a QuerySet of Category, got {type(result).__name__}."
    with CaptureQueriesContext(connection) as ctx:
        for category in category_values():
            _ = category.name, category.value
    assert len(ctx) == 1, (
        f"Reading every category and its value took {len(ctx)} queries; it must be 1. "
        "Do the sum inside the database with annotate(), not in a Python loop.")


def test_result_is_chainable():
    big = category_values().filter(value__gt=500)
    assert [c.name for c in big] == ["Computers"], "The annotation must be usable in a later filter(value__gt=...)."


def test_model_objects_are_returned():
    first = category_values().first()
    assert isinstance(first, Category) and first.name == "Computers", "The result must be Category objects (not dicts): do not use .values()."
