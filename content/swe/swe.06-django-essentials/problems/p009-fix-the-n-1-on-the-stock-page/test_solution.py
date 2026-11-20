import pytest
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext

from solution import Category, Item, Tag

CATEGORIES = ["Audio", "Cables", "Computers", "Office", "Tools"]
TAGS = ["new", "sale", "heavy", "fragile"]


def make_items(first, last):
    """Create items first..last-1 and return the JSON rows the page must show."""
    cats = {name: Category.objects.get_or_create(name=name)[0] for name in CATEGORIES}
    tags = {name: Tag.objects.get_or_create(name=name)[0] for name in TAGS}
    expected = []
    for i in range(first, last):
        category = CATEGORIES[i % 5]
        tag_names = sorted(TAGS[: i % 4])               # 0 to 3 tags
        item = Item.objects.create(name=f"Item {i:02d}", sku=f"S{i:03d}", price="2.50", category=cats[category])
        item.tags.set([tags[n] for n in tag_names])
        expected.append({"name": item.name, "category": category, "tags": tag_names})
    return expected


@pytest.fixture
def client():
    return Client()


def test_json_is_unchanged(client):
    expected = make_items(0, 40)
    r = client.get("/stock/")
    assert r.status_code == 200, f"/stock/ should answer 200, got {r.status_code}. Is the url still in urlpatterns?"
    data = r.json()
    assert data["count"] == 40, f"count must be 40, got {data['count']}."
    assert data["items"] == expected, (
        "The JSON must stay exactly the same: items sorted by name, category name, tag names sorted by name. "
        "Loop over item.tags.all() so that the prefetched, ordered tags are used.")


def test_empty_database(client):
    r = client.get("/stock/")
    assert r.json() == {"count": 0, "items": []}, f"With no items the page must give an empty list, got {r.content!r}."


def test_at_most_three_queries_for_40_items(client):
    make_items(0, 40)
    with CaptureQueriesContext(connection) as ctx:
        r = client.get("/stock/")
    assert r.status_code == 200
    assert len(ctx) <= 3, (
        f"The page ran {len(ctx)} queries for 40 items (limit 3). "
        "Use select_related('category') for the forward foreign key and prefetch_related('tags') for the many-to-many.")


def test_the_number_of_queries_does_not_grow(client):
    make_items(0, 10)
    with CaptureQueriesContext(connection) as ctx10:
        client.get("/stock/")
    make_items(10, 60)
    with CaptureQueriesContext(connection) as ctx60:
        client.get("/stock/")
    assert len(ctx60) == len(ctx10), (
        f"10 items cost {len(ctx10)} queries but 60 items cost {len(ctx60)}: the cost grows with the number of items. "
        "A correct fix costs the same for any number of items.")


def test_tags_are_prefetched_not_requeried(client):
    make_items(0, 40)
    with CaptureQueriesContext(connection) as ctx:
        client.get("/stock/")
    tag_queries = [q for q in ctx.captured_queries if "shop_tag" in q["sql"]]
    assert len(tag_queries) <= 1, (
        f"The tags were fetched with {len(tag_queries)} queries. prefetch_related('tags') needs one; "
        "calling item.tags.order_by(...) or .filter(...) inside the loop throws the prefetch away.")
