from decimal import Decimal

import pytest
from django.db import connection
from django.db.models import QuerySet
from django.test.utils import CaptureQueriesContext

from solution import Category, Item, search

ROWS = [
    # name, sku, quantity, price, status
    ("USB cable", "CB-1", 120, "3.50", "active"),
    ("USB hub", "HB-1", 0, "21.00", "active"),
    ("Keyboard", "KB-1", 10, "49.90", "active"),
    ("Monitor", "MN-1", 3, "189.00", "active"),
    ("Sticker", "FR-1", 5, "0.00", "active"),
    ("Old mouse", "MS-0", 0, "9.00", "discontinued"),
    ("USB dock", "DK-0", 2, "99.00", "discontinued"),
]


@pytest.fixture(autouse=True)
def items():
    category = Category.objects.create(name="Misc")
    for name, sku, quantity, price, status in ROWS:
        Item.objects.create(name=name, sku=sku, quantity=quantity, price=price, status=status, category=category)


def names(qs):
    return [item.name for item in qs]


def test_no_arguments_gives_all_active_items():
    assert names(search()) == ["Keyboard", "Monitor", "Sticker", "USB cable", "USB hub"], (
        "search() with no arguments must return every item that is not discontinued, in the default order (by name). "
        "Use .exclude(status='discontinued').")


def test_discontinued_items_never_appear():
    for found in (search(), search(text="usb"), search(text="mouse"), search(max_price=1000), search(in_stock=False)):
        assert not any(i.status == "discontinued" for i in found), "A discontinued item got into the result: every call must exclude them."


def test_text_matches_name_ignoring_case():
    assert names(search(text="usb")) == ["USB cable", "USB hub"], (
        "text='usb' must find the names that contain it, any case (name__icontains). 'USB dock' is discontinued.")
    assert names(search(text="KEYB")) == ["Keyboard"], "text='KEYB' must match 'Keyboard' (icontains ignores case)."


def test_text_matches_sku_exactly_ignoring_case():
    assert names(search(text="kb-1")) == ["Keyboard"], (
        "text='kb-1' equals the SKU 'KB-1' ignoring case: use Q(sku__iexact=text) joined with | to the name condition.")


def test_sku_is_not_a_substring_search():
    assert names(search(text="kb")) == [], "text='kb' is only part of the SKU 'KB-1': the SKU lookup is iexact, not icontains."


def test_name_and_sku_are_or_not_and():
    assert names(search(text="cb-1")) == ["USB cable"], (
        "'cb-1' matches only the SKU of 'USB cable'; its name does not contain it. The two conditions must be joined with | (OR).")


@pytest.mark.parametrize("value", [None, ""])
def test_empty_text_means_no_filter(value):
    assert len(search(text=value)) == 5, f"text={value!r} must not filter anything: only apply the text rule when text is given."


def test_max_price_is_inclusive():
    assert names(search(max_price=21)) == ["Sticker", "USB cable", "USB hub"], (
        "max_price=21 keeps price <= 21 (price__lte); 'USB hub' costs exactly 21.00 and must stay.")
    assert names(search(max_price=Decimal("3.50"))) == ["Sticker", "USB cable"], "max_price=Decimal('3.50') keeps 3.50 and 0.00."


def test_max_price_zero_is_a_real_value():
    assert names(search(max_price=0)) == ["Sticker"], (
        "max_price=0 means 'free items only', not 'no filter'. Test 'is not None', not 'if max_price:'.")


def test_in_stock_true():
    assert names(search(in_stock=True)) == ["Keyboard", "Monitor", "Sticker", "USB cable"], (
        "in_stock=True keeps quantity > 0 (quantity__gt=0).")


def test_in_stock_false_is_a_real_value():
    assert names(search(in_stock=False)) == ["USB hub"], (
        "in_stock=False keeps quantity == 0 (the active ones). 'if in_stock:' would ignore False: compare with True and False explicitly.")


def test_filters_combine_with_and():
    assert names(search(text="usb", in_stock=True)) == ["USB cable"], "text and in_stock must both apply."
    assert names(search(text="usb", max_price=5, in_stock=True)) == ["USB cable"], "All three filters must apply together."
    assert names(search(text="usb", max_price=5, in_stock=False)) == [], "No active USB item is cheap and out of stock."


def test_returns_a_lazy_queryset():
    with CaptureQueriesContext(connection) as ctx:
        result = search(text="usb", max_price=50, in_stock=True)
    assert len(ctx) == 0, f"search() ran {len(ctx)} queries when it was called. Return the QuerySet without evaluating it (no list(), no len())."
    assert isinstance(result, QuerySet), f"search() must return a QuerySet, got {type(result).__name__}."
    with CaptureQueriesContext(connection) as ctx:
        names(result)
    assert len(ctx) == 1, f"Using the result should cost exactly 1 query, it cost {len(ctx)}."


def test_result_can_be_chained():
    big = search(text="usb").filter(quantity__gt=50)
    assert names(big) == ["USB cable"], "The returned QuerySet must accept further .filter() calls."
    assert search().count() == 5, "The result must support .count()."
