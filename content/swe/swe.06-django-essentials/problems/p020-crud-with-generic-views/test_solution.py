import pytest
from django.test import Client

from solution import Item


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def items():
    return [Item.objects.create(name=n, quantity=q) for n, q in [("pen", 3), ("ink", 9), ("cap", 1)]]


def test_list_is_ordered_by_name(client, items):
    r = client.get("/items/")
    assert r.status_code == 200, (
        f"GET /items/ must be 200, got {r.status_code}. A TemplateDoesNotExist error means template_name is missing or misspelled.")
    body = r.content.decode()
    assert body.index("cap") < body.index("ink") < body.index("pen"), (
        "Items must be listed ordered by name (cap, ink, pen): set ordering = ['name'] on the view.")
    assert "pen (3)" in body, "The list template shows each item as 'name (quantity)'."


def test_empty_list_is_still_200(client):
    assert client.get("/items/").status_code == 200, "An empty list is not an error."


def test_detail_shows_one_item(client, items):
    r = client.get(f"/items/{items[0].pk}/")
    assert r.status_code == 200, f"GET /items/<pk>/ must be 200, got {r.status_code}. Check model and template_name."
    body = r.content.decode()
    assert "<h1>pen</h1>" in body and "quantity 3" in body, f"The detail page must show the item, got {body!r}."


@pytest.mark.parametrize("url", ["/items/999/", "/items/999/edit/"])
def test_unknown_pk_is_404(client, items, url):
    assert client.get(url).status_code == 404, (
        f"{url} must be 404: DetailView and UpdateView call get_object_or_404 for you, so do not catch the error.")


def test_create_form_is_shown(client):
    r = client.get("/items/new/")
    assert r.status_code == 200, f"GET /items/new/ must be 200, got {r.status_code}."
    body = r.content.decode()
    assert 'name="name"' in body and 'name="quantity"' in body, "The form must have exactly the fields name and quantity: set fields = ['name', 'quantity']."


def test_valid_create_saves_and_redirects(client):
    r = client.post("/items/new/", {"name": "Pen", "quantity": 3})
    assert r.status_code == 302, f"A valid POST must redirect, got {r.status_code}."
    assert r["Location"] == "/items/", f"success_url must be reverse_lazy('item_list') = /items/, got {r['Location']!r}."
    assert [(i.name, i.quantity) for i in Item.objects.all()] == [("Pen", 3)], "One item must be saved."


def test_invalid_create_shows_the_form_again(client):
    r = client.post("/items/new/", {"name": "", "quantity": "x"})
    assert r.status_code == 200, f"An invalid POST must re-show the form (200), got {r.status_code}."
    assert "errorlist" in r.content.decode(), "The page must contain the form errors."
    assert Item.objects.count() == 0, "Nothing may be saved."


def test_update_form_is_filled(client, items):
    r = client.get(f"/items/{items[0].pk}/edit/")
    assert r.status_code == 200, f"GET /items/<pk>/edit/ must be 200, got {r.status_code}."
    body = r.content.decode()
    assert 'value="pen"' in body and 'value="3"' in body, "The edit form must be filled with the item's current values."


def test_valid_update_changes_the_row_and_redirects(client, items):
    pen = items[0]
    r = client.post(f"/items/{pen.pk}/edit/", {"name": "pen2", "quantity": 8})
    assert r.status_code == 302 and r["Location"] == "/items/", f"A valid update must redirect to /items/, got {r.status_code} {r.get('Location')}."
    pen.refresh_from_db()
    assert (pen.name, pen.quantity) == ("pen2", 8), "The existing row must be changed (not a new one created)."
    assert Item.objects.count() == 3, "Updating must not add rows."


def test_invalid_update_changes_nothing(client, items):
    pen = items[0]
    r = client.post(f"/items/{pen.pk}/edit/", {"name": "", "quantity": 8})
    assert r.status_code == 200, f"An invalid update must re-show the form (200), got {r.status_code}."
    pen.refresh_from_db()
    assert (pen.name, pen.quantity) == ("pen", 3), "An invalid update must leave the row unchanged."


def test_success_url_is_lazy_reverse():
    from solution import ItemCreateView, ItemUpdateView
    for view in (ItemCreateView, ItemUpdateView):
        assert str(view.success_url) == "/items/", f"{view.__name__}.success_url must reverse to /items/, got {view.success_url!r}."
