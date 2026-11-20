import pytest
from django.db import connection
from django.db.models import QuerySet
from django.test.utils import CaptureQueriesContext

from solution import Category, Item


@pytest.fixture
def data():
    pens = Category.objects.create(name="Pens", slug="pens")
    hats = Category.objects.create(name="Hats", slug="hats")
    Item.objects.create(name="pen", quantity=2, active=True, category=pens)
    Item.objects.create(name="ink", quantity=9, active=True, category=pens)
    Item.objects.create(name="cap", quantity=1, active=False, category=hats)
    Item.objects.create(name="hat", quantity=5, active=True, category=hats)
    return pens, hats


def names(qs):
    return sorted(i.name for i in qs)


def test_low_stock_is_strictly_below(data):
    assert names(Item.objects.low_stock(5)) == ["cap", "pen"], (
        "low_stock(5) means quantity < 5: pen (2) and cap (1). The hat has exactly 5 and is not low.")
    assert names(Item.objects.low_stock(6)) == ["cap", "hat", "pen"], "With threshold 6 the hat (5) is low too."
    assert names(Item.objects.low_stock(0)) == [], "Nothing is below 0."


def test_active(data):
    assert names(Item.objects.active()) == ["hat", "ink", "pen"], "active() keeps active=True: cap is inactive."


def test_in_category(data):
    assert names(Item.objects.in_category("pens")) == ["ink", "pen"], "in_category('pens') uses category__slug."
    assert names(Item.objects.in_category("nope")) == [], "An unknown slug gives an empty queryset, not an error."


def test_methods_return_querysets(data):
    for qs in (Item.objects.low_stock(5), Item.objects.active(), Item.objects.in_category("pens")):
        assert isinstance(qs, QuerySet), f"Each method must return a QuerySet (use self.filter(...)), got {type(qs).__name__}."


def test_chaining_in_every_order(data):
    expected = ["pen"]
    chains = [
        Item.objects.active().low_stock(5).in_category("pens"),
        Item.objects.in_category("pens").low_stock(5).active(),
        Item.objects.low_stock(5).in_category("pens").active(),
        Item.objects.filter(name__startswith="p").active().low_stock(5),
    ]
    for chain in chains:
        assert names(chain) == expected, (
            f"A chain in any order must give {expected}, got {names(chain)}. "
            "A method on the QuerySet class can be called on the result of any other QuerySet method.")


def test_works_on_a_queryset_made_by_filter(data):
    qs = Item.objects.filter(quantity__gte=0).low_stock(3)
    assert names(qs) == ["cap", "pen"], "low_stock must also be callable after filter(): put it on the QuerySet, not on a Manager subclass."


def test_works_on_the_related_manager(data):
    pens, hats = data
    assert names(pens.items.low_stock(5)) == ["pen"], "category.items.low_stock(5) must work (as_manager copies the methods)."
    assert names(hats.items.active().low_stock(10)) == ["hat"], "category.items.active().low_stock(10) must give only the hat."


def test_building_a_chain_does_not_query_and_reading_it_queries_once(data):
    with CaptureQueriesContext(connection) as ctx:
        chain = Item.objects.active().low_stock(5).in_category("pens")
    assert len(ctx) == 0, f"Building a chain must not touch the database (QuerySets are lazy), it ran {len(ctx)} queries."
    with CaptureQueriesContext(connection) as ctx:
        list(chain)
    assert len(ctx) == 1, f"Reading the chain should be exactly one query, got {len(ctx)}."


def test_the_manager_is_built_from_the_queryset(data):
    from solution import ItemQuerySet
    assert isinstance(Item.objects.all(), ItemQuerySet), "Item.objects must be ItemQuerySet.as_manager(), so .all() is an ItemQuerySet."
