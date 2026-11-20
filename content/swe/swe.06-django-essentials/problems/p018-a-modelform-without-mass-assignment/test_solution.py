from decimal import Decimal

import pytest

from solution import Category, Item, ItemForm


@pytest.fixture
def cat():
    return Category.objects.create(name="Writing")


def data(cat, **over):
    d = {"name": "Pen", "sku": "AB-123", "price": "1.50", "category": cat.pk}
    d.update(over)
    return d


def test_the_fields_are_an_explicit_allow_list():
    assert list(ItemForm().fields) == ["name", "sku", "price", "category"], (
        f"The form must have exactly name, sku, price, category (in this order), got {list(ItemForm().fields)}. "
        "Use fields = [...] in Meta.")
    assert ItemForm._meta.exclude is None, "Do not use exclude: a field added to the model later would become editable by every visitor."


def test_a_valid_form_creates_an_item_with_default_quantity(cat):
    form = ItemForm(data(cat, quantity=999))
    assert form.is_valid(), f"A valid POST must pass, errors: {form.errors.as_json()}"
    item = form.save()
    assert (item.name, item.sku, item.price, item.category_id) == ("Pen", "AB-123", Decimal("1.50"), cat.pk)
    assert item.quantity == 0, "A posted quantity must be ignored: quantity is not in the allow-list, so the default 0 stays."


def test_mass_assignment_on_an_existing_item_changes_nothing(cat):
    item = Item.objects.create(name="Pen", sku="AB-123", price="1.50", quantity=7, category=cat)
    form = ItemForm(data(cat, name="Pen 2", quantity=999), instance=item)
    assert form.is_valid(), f"errors: {form.errors.as_json()}"
    form.save()
    item.refresh_from_db()
    assert item.name == "Pen 2", "The allowed fields must still be saved."
    assert item.quantity == 7, "quantity=999 in the POST must not change the stock (7)."


def test_sku_is_stripped_and_upper_cased(cat):
    form = ItemForm(data(cat, sku="  pen-00042 "))
    assert form.is_valid(), f"errors: {form.errors.as_json()}"
    assert form.cleaned_data["sku"] == "PEN-00042", f"clean_sku must return the stripped, upper-case value, got {form.cleaned_data['sku']!r}."
    assert form.save().sku == "PEN-00042", "The saved sku must be the cleaned one."


@pytest.mark.parametrize("bad", ["abc", "A-123", "ABCDE-123", "AB-12", "AB-123456", "AB123", "12-345", "AB-12a", "AB 123", ""])
def test_bad_skus_are_refused_on_the_sku_field(cat, bad):
    form = ItemForm(data(cat, sku=bad))
    assert not form.is_valid(), f"{bad!r} does not match 2-4 letters, hyphen, 3-5 digits and must be refused."
    assert "sku" in form.errors, f"The error for {bad!r} must be attached to the sku field (raise ValidationError in clean_sku), got {list(form.errors)}."


@pytest.mark.parametrize("good", ["AB-123", "ab-123", "ABCD-12345", "pen-001"])
def test_good_skus_pass(cat, good):
    assert ItemForm(data(cat, sku=good)).is_valid(), f"{good!r} matches the pattern (after upper-casing) and must pass."


def test_uniqueness_is_checked_after_cleaning(cat):
    Item.objects.create(name="Pen", sku="AB-123", price="1.50", category=cat)
    form = ItemForm(data(cat, sku="ab-123"))
    assert not form.is_valid(), "'ab-123' becomes 'AB-123', which already exists: the form must be invalid, not crash with IntegrityError later."
    assert "sku" in form.errors, f"The duplicate must be reported on sku, got {list(form.errors)}."


def test_editing_an_item_may_keep_its_own_sku(cat):
    item = Item.objects.create(name="Pen", sku="AB-123", price="1.50", category=cat)
    form = ItemForm(data(cat, name="Pen 2", sku="ab-123"), instance=item)
    assert form.is_valid(), f"An item must not clash with itself, errors: {form.errors.as_json()}"


def test_other_fields_are_still_validated(cat):
    form = ItemForm(data(cat, price="abc", name=""))
    assert not form.is_valid() and {"price", "name"} <= set(form.errors), f"price and name errors expected, got {list(form.errors)}."
    assert not ItemForm(data(cat, category=9999)).is_valid(), "An unknown category id must be refused."
