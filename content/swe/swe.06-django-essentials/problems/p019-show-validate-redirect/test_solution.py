import re

import pytest
from django.test import Client

from solution import Item

URL = "/items/new/"
GOOD = {"name": "Pen", "sku": "AB-1", "price": "1.50"}


@pytest.fixture
def client():
    return Client(enforce_csrf_checks=True)


def token_of(client):
    """GET the form like a browser: read the hidden field from the page and the cookie is kept by the client."""
    r = client.get(URL)
    assert r.status_code == 200, f"GET {URL} must answer 200, got {r.status_code}. Is item_create in urlpatterns?"
    m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.content.decode())
    assert m, "The page must contain the hidden csrfmiddlewaretoken input: render the form with the request ({% csrf_token %})."
    assert "csrftoken" in client.cookies, "The response to the GET must set the csrftoken cookie."
    return m.group(1)


def test_get_shows_the_empty_form(client):
    r = client.get(URL)
    assert r.status_code == 200, f"GET must be 200, got {r.status_code}."
    body = r.content.decode()
    for field in ("name", "sku", "price"):
        assert f'name="{field}"' in body, f"The page must contain an input called {field!r}."
    assert Item.objects.count() == 0, "A GET must not create anything."


def test_post_without_the_token_is_refused_by_csrf(client):
    r = client.post(URL, GOOD)
    assert r.status_code == 403, f"A POST without a CSRF token must be 403 (the middleware does it), got {r.status_code}."
    assert Item.objects.count() == 0, "Nothing may be saved when CSRF fails."


def test_post_with_a_wrong_token_is_refused(client):
    token_of(client)
    r = client.post(URL, {**GOOD, "csrfmiddlewaretoken": "wrong" * 13})
    assert r.status_code == 403, f"A wrong token must give 403, got {r.status_code}."


def test_valid_post_saves_and_redirects(client):
    token = token_of(client)
    r = client.post(URL, {**GOOD, "csrfmiddlewaretoken": token})
    assert r.status_code == 302, f"A valid POST must redirect (302), got {r.status_code}. Return redirect('item_list') after form.save()."
    assert r["Location"] == "/items/", f"The redirect must go to the list page /items/, got {r['Location']!r}."
    assert Item.objects.count() == 1 and Item.objects.get().sku == "AB-1", "Exactly one Item must be saved."
    assert client.get(r["Location"]).json() == {"items": ["AB-1"]}, "The list page must show the new item."


def test_invalid_post_shows_the_form_again_with_errors(client):
    token = token_of(client)
    r = client.post(URL, {"name": "Pen typed", "sku": "AB-1", "price": "abc", "csrfmiddlewaretoken": token})
    assert r.status_code == 200, f"An invalid POST must re-show the form with status 200 (not a redirect), got {r.status_code}."
    body = r.content.decode()
    assert "errorlist" in body, "The page must show the errors of the form: render the bound form (the one with request.POST), not a new empty one."
    assert 'value="Pen typed"' in body, "The values the user typed must still be in the inputs (use the bound form)."
    assert Item.objects.count() == 0, "Invalid data must not be saved."


def test_every_required_field_is_checked(client):
    token = token_of(client)
    r = client.post(URL, {"csrfmiddlewaretoken": token})
    assert r.status_code == 200 and r.content.decode().count("errorlist") >= 1, "An empty POST must re-show the form with errors."
    assert Item.objects.count() == 0


def test_a_duplicate_sku_is_a_form_error_not_a_crash(client):
    Item.objects.create(name="Old", sku="AB-1", price="1.00")
    token = token_of(client)
    r = client.post(URL, {**GOOD, "csrfmiddlewaretoken": token})
    assert r.status_code == 200, f"A duplicate sku must come back as a form error (200), got {r.status_code}."
    assert Item.objects.count() == 1, "The duplicate must not be saved."


def test_posting_twice_creates_two_different_items(client):
    token = token_of(client)
    client.post(URL, {**GOOD, "csrfmiddlewaretoken": token})
    r = client.post(URL, {**GOOD, "sku": "AB-2", "csrfmiddlewaretoken": token})
    assert r.status_code == 302 and Item.objects.count() == 2, "A second valid POST with a new sku must also redirect and save."


@pytest.mark.parametrize("method", ["put", "delete", "patch"])
def test_other_methods_are_405(client, method):
    r = getattr(client, method)(URL)
    assert r.status_code in (405, 403), f"{method.upper()} must not be accepted, got {r.status_code}."
    # 403 can come from CSRF first; the real check follows with a client that does not enforce CSRF
    r2 = getattr(Client(), method)(URL)
    assert r2.status_code == 405, f"{method.upper()} must give 405 Method Not Allowed (require_http_methods), got {r2.status_code}."
