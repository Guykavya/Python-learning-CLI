import json

from solution import Catalog


def test_key_format():
    assert Catalog.key(7) == "product:v1:7", "Keys are namespace + version + id: 'product:v1:7'."


def test_repeated_reads_hit_the_cache(db, r):
    catalog = Catalog(db, r)
    for _ in range(5):
        product = catalog.get_product(1)
    assert product == {"id": 1, "name": "Keyboard", "price_cents": 4990}
    assert db.reads == 1, f"5 reads of one product must reach the database once, got {db.reads}. Do you store the result after a miss?"


def test_value_is_json_with_ttl(db, r):
    Catalog(db, r).get_product(1)
    raw = r.get("product:v1:1")
    assert raw is not None, "After a miss the product must be stored under 'product:v1:1'."
    assert json.loads(raw) == {"id": 1, "name": "Keyboard", "price_cents": 4990}, "Store the product as JSON text (json.dumps)."
    assert r.ttl("product:v1:1") == 300, "A found product is cached for ttl=300 seconds. Every cache entry needs a TTL."


def test_found_entry_expires(db, r, clock):
    catalog = Catalog(db, r)
    catalog.get_product(1)
    clock.advance(299)
    catalog.get_product(1)
    assert db.reads == 1, "Still within the 300 s TTL: no database read."
    clock.advance(1)
    catalog.get_product(1)
    assert db.reads == 2, "After 300 s the entry expired: the next read reloads."


def test_not_found_is_cached_briefly(db, r, clock):
    catalog = Catalog(db, r)
    for _ in range(4):
        assert catalog.get_product(99) is None, "A missing product gives None."
    assert db.reads == 1, f"4 reads of a missing product must reach the database ONCE (negative caching), got {db.reads}."
    assert r.get("product:v1:99") == "null", "'Not found' is cached as the JSON text null."
    assert r.ttl("product:v1:99") == 30, "Negative entries get the SHORT missing_ttl (30 s), so new products appear quickly."
    clock.advance(30)
    catalog.get_product(99)
    assert db.reads == 2, "After missing_ttl the 'not found' entry expired, so the database is asked again."


def test_custom_ttls(db, r):
    catalog = Catalog(db, r, ttl=60, missing_ttl=5)
    catalog.get_product(1)
    catalog.get_product(42)
    assert (r.ttl("product:v1:1"), r.ttl("product:v1:42")) == (60, 5), "Use the ttl and missing_ttl given to the constructor."


def test_update_invalidates(db, r):
    catalog = Catalog(db, r)
    catalog.get_product(1)
    catalog.update_price(1, 3990)
    assert db.rows[1]["price_cents"] == 3990, "update_price must change the database."
    assert r.get("product:v1:1") is None, "After a write the cached key must be deleted."
    assert catalog.get_product(1)["price_cents"] == 3990, "The next read must see the new price."
    assert db.reads == 2


def test_update_order_database_first(db, r):
    order = []

    class Spy:
        def __init__(self, inner):
            self.inner = inner

        def __getattr__(self, name):
            return getattr(self.inner, name)

    cache, store = Spy(r), Spy(db)
    cache.delete = lambda *k: (order.append("cache.delete"), r.delete(*k))[1]
    store.update_price = lambda *a: (order.append("db.update"), db.update_price(*a))[1]
    Catalog(store, cache).update_price(1, 100)
    assert order == ["db.update", "cache.delete"], \
        f"Change the database FIRST, then delete the key (got {order}). Deleting first lets a reader re-cache the old price."


def test_create_clears_cached_not_found(db, r):
    catalog = Catalog(db, r)
    assert catalog.get_product(3) is None
    catalog.create_product(3, "Mouse", 1500)
    assert catalog.get_product(3) == {"id": 3, "name": "Mouse", "price_cents": 1500}, \
        "A new product must be visible at once: create_product must delete the cached 'not found'."


def test_never_pickle(db, r):
    Catalog(db, r).get_product(2)
    raw = r.get("product:v1:2")
    assert isinstance(raw, str) and raw.startswith("{"), "The cached value must be JSON text, never pickle bytes."
