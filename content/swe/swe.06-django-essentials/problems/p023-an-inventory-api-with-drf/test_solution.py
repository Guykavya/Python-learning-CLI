import pytest
from django.contrib.auth.models import User
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from solution import Category, Item


@pytest.fixture
def category():
    return Category.objects.create(name="Cables")


@pytest.fixture
def api():
    client = APIClient()
    client.force_authenticate(User.objects.create_user("sam", password="pw-sam-12345"))
    return client


def payload(category, **changes):
    data = {"name": "Gadget", "sku": "GD-1", "price": "9.99", "category": category.pk}
    data.update(changes)
    return data


def test_anonymous_is_refused(category):
    anon = APIClient()
    r = anon.get("/api/items/")
    assert r.status_code == 403, (
        f"An anonymous GET must be refused with 403 (SessionAuthentication cannot challenge), got {r.status_code}. "
        "Set permission_classes = [IsAuthenticated] on the viewset, and register the router under path('api/', ...).")
    r = anon.post("/api/items/", payload(category), format="json")
    assert r.status_code == 403, f"An anonymous POST must be 403, got {r.status_code}."
    assert Item.objects.count() == 0, "Nothing may be created for an anonymous request."


def test_create_returns_201_and_ignores_quantity(api, category):
    r = api.post("/api/items/", payload(category, quantity=999), format="json")
    assert r.status_code == 201, f"A valid POST must answer 201, got {r.status_code} {r.content!r}."
    body = r.json()
    assert body["quantity"] == 0, (
        f"quantity must be read-only: the new item must have 0 even if 999 was sent, got {body['quantity']!r}. "
        "Use read_only_fields = ['quantity'].")
    assert Item.objects.get(pk=body["id"]).quantity == 0, "The database row must also have quantity 0."
    assert body["price"] == "9.99", f"price must be written as a string '9.99' (DecimalField), got {body['price']!r}."
    assert body["category"] == category.pk, "category must be the id of the category."
    assert body["category_name"] == "Cables", "category_name must come from source='category.name' (read-only)."


@pytest.mark.parametrize("price", ["-1", "0", "-0.01"])
def test_price_must_be_above_zero(api, category, price):
    r = api.post("/api/items/", payload(category, price=price), format="json")
    assert r.status_code == 400, f"price {price} must be rejected with 400, got {r.status_code}. Write validate_price(self, value)."
    assert "price" in r.json(), f"The error must be listed under the key 'price', got {r.json()!r}."
    assert set(r.json()) == {"price"}, f"Only the price field is wrong; other keys should not appear: {r.json()!r}."
    assert Item.objects.count() == 0, "A rejected request must not create a row."


def test_other_fields_are_validated(api, category):
    r = api.post("/api/items/", {"sku": "X-1", "price": "1.00", "category": category.pk}, format="json")
    assert r.status_code == 400 and "name" in r.json(), f"A missing name must give 400 with an error under 'name', got {r.status_code} {r.content!r}."
    api.post("/api/items/", payload(category), format="json")
    r = api.post("/api/items/", payload(category, name="Other"), format="json")
    assert r.status_code == 400 and "sku" in r.json(), (
        f"A duplicate sku must give 400 with an error under 'sku' (ModelSerializer adds the unique check), got {r.status_code} {r.content!r}.")


def test_list_uses_one_query(api, category):
    other = Category.objects.create(name="Chargers")
    for i in range(12):
        Item.objects.create(name=f"Item {i}", sku=f"S-{i}", price="1.50", category=category if i % 2 else other)
    with CaptureQueriesContext(connection) as ctx:
        r = api.get("/api/items/")
    assert r.status_code == 200, f"List must answer 200, got {r.status_code}."
    data = r.json()
    assert isinstance(data, list) and len(data) == 12, f"No pagination is configured: the list must be a plain JSON list of 12, got {type(data).__name__}."
    assert {row["category_name"] for row in data} == {"Cables", "Chargers"}, "Every row needs category_name."
    assert len(ctx) == 1, (
        f"Listing 12 items must take 1 query, got {len(ctx)}. category_name reads item.category: "
        "use queryset = Item.objects.select_related('category') to avoid one query per item (N+1).")


def test_patch_changes_price_but_not_quantity(api, category):
    item = Item.objects.create(name="Cable", sku="C-1", quantity=4, price="2.00", category=category)
    r = api.patch(f"/api/items/{item.pk}/", {"price": "3.50", "quantity": 1000}, format="json")
    assert r.status_code == 200, f"PATCH must answer 200 (read-only input is ignored, not an error), got {r.status_code}."
    item.refresh_from_db()
    assert str(item.price) == "3.50", f"The price must be updated to 3.50, got {item.price}."
    assert item.quantity == 4, f"quantity must stay 4 (read-only), got {item.quantity}. Stock changes go through movements, not through the API fields."
    r = api.patch(f"/api/items/{item.pk}/", {"price": "-5"}, format="json")
    assert r.status_code == 400, "validate_price must also run on PATCH."


def test_detail_and_delete(api, category):
    item = Item.objects.create(name="Cable", sku="C-1", price="2.00", category=category)
    assert api.get(f"/api/items/{item.pk}/").json()["sku"] == "C-1", "Detail must return the item."
    assert api.get("/api/items/99999/").status_code == 404, "An unknown id must be 404."
    assert api.delete(f"/api/items/{item.pk}/").status_code == 204, "DELETE must answer 204."
    assert Item.objects.count() == 0, "The item must be gone."
