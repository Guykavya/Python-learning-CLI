from decimal import Decimal

import pytest
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import IntegrityError, models, transaction
from django.db.models import ProtectedError

from solution import Category, Item


def field(model, name):
    try:
        return model._meta.get_field(name)
    except FieldDoesNotExist:
        pytest.fail(f"{model.__name__} has no field called {name!r}. Add it as a class attribute of the model.")


def test_category_name_field():
    f = field(Category, "name")
    assert isinstance(f, models.CharField), "Category.name must be a CharField."
    assert f.max_length == 60, f"Category.name needs max_length=60, got {f.max_length}."
    assert f.unique, "Category.name must be unique=True: two categories with the same name make no sense."


def test_item_char_fields():
    name, sku = field(Item, "name"), field(Item, "sku")
    assert isinstance(name, models.CharField) and name.max_length == 100, "Item.name: CharField with max_length=100."
    assert name.unique, "Item.name must be unique=True."
    assert isinstance(sku, models.CharField) and sku.max_length == 20, "Item.sku: CharField with max_length=20."
    assert sku.unique, "Item.sku must be unique=True: the SKU identifies the item."


def test_quantity_field():
    q = field(Item, "quantity")
    assert isinstance(q, models.PositiveIntegerField), (
        f"Item.quantity must be a PositiveIntegerField (a stock level is never negative), got {type(q).__name__}.")
    assert q.default == 0, f"Item.quantity needs default=0, got {q.default!r}."


def test_price_is_a_decimal_not_a_float():
    p = field(Item, "price")
    assert not isinstance(p, models.FloatField), "Money in a FloatField gives rounding errors. Use DecimalField."
    assert isinstance(p, models.DecimalField), f"Item.price must be a DecimalField, got {type(p).__name__}."
    assert (p.max_digits, p.decimal_places) == (8, 2), (
        f"Item.price needs max_digits=8, decimal_places=2, got ({p.max_digits}, {p.decimal_places}).")


def test_category_foreign_key():
    c = field(Item, "category")
    assert isinstance(c, models.ForeignKey), "Item.category must be a ForeignKey."
    assert c.related_model is Category, "Item.category must point to Category."
    assert c.remote_field.on_delete is models.PROTECT, (
        "Item.category needs on_delete=models.PROTECT: a category that still has items must not be deletable.")
    assert c.remote_field.related_name == "items", 'Use related_name="items" so that category.items works.'


def test_status_choices():
    assert hasattr(Item, "Status"), "Define an inner class Status(models.TextChoices) inside Item."
    s = field(Item, "status")
    assert isinstance(s, models.CharField) and s.max_length == 20, "Item.status: CharField with max_length=20."
    values = [value for value, label in s.choices]
    assert values == ["active", "discontinued"], f"The stored values must be 'active' and 'discontinued' (in this order), got {values}."
    labels = [label for value, label in s.choices]
    assert labels == ["Active", "Discontinued"], f"The labels must be 'Active' and 'Discontinued', got {labels}."
    assert s.default == "active", f"The default status is Status.ACTIVE ('active'), got {s.default!r}."
    assert Item.Status.ACTIVE == "active" and Item.Status.DISCONTINUED == "discontinued", "Check the values of the Status members."


def test_meta_options():
    assert Category._meta.app_label == "shop" and Item._meta.app_label == "shop", 'Both models need class Meta: app_label = "shop".'
    assert list(Category._meta.ordering) == ["name"], f"Category.Meta.ordering must be ['name'], got {list(Category._meta.ordering)}."
    assert list(Item._meta.ordering) == ["name"], f"Item.Meta.ordering must be ['name'], got {list(Item._meta.ordering)}."


def test_str_methods():
    cables = Category(name="Cables")
    assert str(cables) == "Cables", f"str(category) must be the name, got {str(cables)!r}. Define __str__."
    item = Item(name="USB cable", sku="CB-1")
    assert str(item) == "USB cable (CB-1)", f"str(item) must be 'USB cable (CB-1)', got {str(item)!r}."


def test_create_and_defaults():
    cables = Category.objects.create(name="Cables")
    item = Item.objects.create(name="USB cable", sku="CB-1", price="3.50", category=cables)
    item.refresh_from_db()
    assert item.quantity == 0, f"quantity must default to 0, got {item.quantity!r}."
    assert item.status == "active", f"status must default to 'active', got {item.status!r}."
    assert item.price == Decimal("3.50"), f"price must come back as Decimal('3.50'), got {item.price!r}."
    assert list(cables.items.all()) == [item], "category.items must list the category's items (related_name='items')."


def test_default_ordering_is_by_name():
    c = Category.objects.create(name="Misc")
    for name, sku in [("Zip", "Z"), ("Apple", "A"), ("Mouse", "M")]:
        Item.objects.create(name=name, sku=sku, price="1", category=c)
    assert [i.name for i in Item.objects.all()] == ["Apple", "Mouse", "Zip"], "Item.objects.all() must be sorted by name (Meta.ordering)."
    Category.objects.create(name="Audio")
    assert [x.name for x in Category.objects.all()] == ["Audio", "Misc"], "Category.objects.all() must be sorted by name."


def test_unique_sku_and_name_are_enforced_by_the_database():
    c = Category.objects.create(name="Misc")
    Item.objects.create(name="One", sku="S1", price="1", category=c)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Item.objects.create(name="Two", sku="S1", price="1", category=c)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Item.objects.create(name="One", sku="S2", price="1", category=c)


def test_protected_category():
    c = Category.objects.create(name="Misc")
    Item.objects.create(name="One", sku="S1", price="1", category=c)
    with pytest.raises(ProtectedError):
        c.delete()
    assert Category.objects.filter(pk=c.pk).exists(), "The category must still exist after the refused delete."
    Item.objects.all().delete()
    c.delete()
    assert not Category.objects.exists(), "After the items are gone the category can be deleted."


def test_invalid_status_is_caught_by_full_clean():
    c = Category.objects.create(name="Misc")
    item = Item(name="One", sku="S1", price="1", category=c, status="lost")
    with pytest.raises(ValidationError) as info:
        item.full_clean()
    assert "status" in info.value.message_dict, "full_clean() must complain about status='lost': set choices=Status on the field."
