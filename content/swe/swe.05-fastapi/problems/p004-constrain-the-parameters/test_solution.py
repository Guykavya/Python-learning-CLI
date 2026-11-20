import pytest
from fastapi.testclient import TestClient

from solution import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def errors(response):
    """The (loc, type) pairs of a 422 response."""
    assert response.status_code == 422, f"Expected a 422, got {response.status_code}: {response.text}"
    return [(e["loc"], e["type"]) for e in response.json()["detail"]]


def test_defaults(client):
    r = client.get("/shops/3/products")
    assert r.status_code == 200, f"A plain call must work, got {r.status_code}: {r.text}"
    assert r.json() == {"shop_id": 3, "q": None, "page": 1, "size": 10, "tags": []}, f"Wrong defaults: {r.json()}"


def test_good_values(client):
    r = client.get("/shops/3/products", params={"q": "red shoe", "page": 2, "size": 50})
    assert r.status_code == 200, f"q='red shoe', page=2, size=50 are all allowed, got {r.status_code}: {r.text}"
    assert r.json() == {"shop_id": 3, "q": "red shoe", "page": 2, "size": 50, "tags": []}


def test_tag_list_collects_every_value(client):
    r = client.get("/shops/3/products?tag=sale&tag=new&tag=kids")
    assert r.status_code == 200, r.text
    assert r.json()["tags"] == ["sale", "new", "kids"], (
        f"Got tags={r.json()['tags']!r}. A repeated query key needs a list type AND Query(): "
        "tag: Annotated[list[str] | None, Query()] = None (without Query() a list is read from the body).")


def test_boundaries_are_allowed(client):
    r = client.get("/shops/1/products", params={"q": "ab", "page": 1, "size": 1})
    assert r.status_code == 200, f"shop_id=1, q of 2 chars, page=1, size=1 are the smallest allowed values: {r.text}"
    r = client.get("/shops/1/products", params={"q": "a" * 30})
    assert r.status_code == 200, "A q of exactly 30 characters is allowed (max_length=30)."


@pytest.mark.parametrize("url, loc, kind, why", [
    ("/shops/0/products", ["path", "shop_id"], "greater_than_equal", "shop_id must be at least 1: Path(ge=1)"),
    ("/shops/x/products", ["path", "shop_id"], "int_parsing", "shop_id is an int"),
    ("/shops/3/products?page=0", ["query", "page"], "greater_than_equal", "page must be at least 1: Query(ge=1)"),
    ("/shops/3/products?size=0", ["query", "size"], "greater_than_equal", "size must be at least 1"),
    ("/shops/3/products?size=51", ["query", "size"], "less_than_equal", "size is at most 50: Query(ge=1, le=50)"),
    ("/shops/3/products?q=a", ["query", "q"], "string_too_short", "q needs at least 2 characters: min_length=2"),
    ("/shops/3/products?q=" + "a" * 31, ["query", "q"], "string_too_long", "q has at most 30 characters: max_length=30"),
    ("/shops/3/products?q=Shoe", ["query", "q"], "string_pattern_mismatch", "q allows only a-z, 0-9 and spaces: pattern='^[a-z0-9 ]+$'"),
    ("/shops/3/products?q=shoe!", ["query", "q"], "string_pattern_mismatch", "'!' is not allowed by the pattern"),
])
def test_each_bad_value_is_a_422(client, url, loc, kind, why):
    found = errors(client.get(url))
    assert (loc, kind) in found, f"{url}: expected an error at {loc} of type {kind!r} ({why}); got {found}"


def test_all_errors_come_together(client):
    found = errors(client.get("/shops/0/products?size=51&q=X"))
    locs = [loc for loc, _ in found]
    assert ["path", "shop_id"] in locs and ["query", "size"] in locs and ["query", "q"] in locs, (
        f"Three bad values must give three errors in ONE 422 response; got {found}")
