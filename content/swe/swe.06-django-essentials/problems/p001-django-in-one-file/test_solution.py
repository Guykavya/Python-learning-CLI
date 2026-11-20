import pytest
from django.test import Client


@pytest.fixture
def client():
    return Client()


def test_home_is_plain_text(client):
    r = client.get("/")
    assert r.status_code == 200, f"GET / should answer 200, got {r.status_code}. Is there a path('', home) entry in urlpatterns?"
    assert r.content == b"Welcome", f"The body must be exactly 'Welcome', got {r.content!r}."
    assert r["Content-Type"].startswith("text/plain"), (
        f"home must send Content-Type text/plain (pass content_type='text/plain' to HttpResponse), got {r['Content-Type']!r}.")


@pytest.mark.parametrize("pk", [1, 42, 0, 123456])
def test_item_detail_gets_an_int(client, pk):
    r = client.get(f"/items/{pk}/")
    assert r.status_code == 200, f"/items/{pk}/ should be 200, got {r.status_code}. Use path('items/<int:pk>/', item_detail)."
    assert r.json() == {"id": pk, "kind": "item"}, (
        f"Expected {{'id': {pk}, 'kind': 'item'}} with id as an int, got {r.content!r}. "
        "The <int:pk> converter passes an int to the view; JsonResponse then writes a JSON number.")


@pytest.mark.parametrize("url", ["/items/abc/", "/items/-1/", "/items/1.5/", "/items/"])
def test_non_matching_item_urls_are_404(client, url):
    r = client.get(url)
    assert r.status_code == 404, (
        f"{url} must not reach item_detail and must be a 404, got {r.status_code}. "
        "The int converter matches digits only, and the pattern ends with a slash.")


def test_missing_final_slash_is_redirected_not_404(client):
    r = client.get("/items/7")
    assert r.status_code == 301 and r["Location"] == "/items/7/", (
        f"/items/7 (no final slash) should be redirected to /items/7/ by CommonMiddleware (APPEND_SLASH), got {r.status_code}. "
        "Keep the final slash in the pattern: path('items/<int:pk>/', ...).")


def test_article_slug(client):
    r = client.get("/articles/learn-django-fast/")
    assert r.status_code == 200, f"/articles/learn-django-fast/ should be 200, got {r.status_code}. Use <slug:slug>."
    assert r.json() == {"slug": "learn-django-fast", "title": "Learn Django Fast"}, (
        f"Expected the slug and a title made from it (hyphens to spaces, each word capitalised), got {r.content!r}.")


@pytest.mark.parametrize("url", ["/articles/has space/", "/articles/a.b/", "/articles/a/b/"])
def test_bad_slugs_are_404(client, url):
    assert client.get(url).status_code == 404, f"{url} is not a slug (letters, digits, - and _ only): expected 404."


def test_unknown_url_is_404(client):
    assert client.get("/nope/").status_code == 404, "A URL that matches no path() entry is a 404."
