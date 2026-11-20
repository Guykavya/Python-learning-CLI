# A catalogue behind a cache

Chapter sections 4.1 and 4.2 (cache-aside), and "Try it: why the 404 is cached". Put a Redis cache in front of a product database using the **cache-aside** pattern: look in the cache; on a miss, load from the database and store the answer; on a write, change the database and then delete the cached key.

## What to write

```python
class Catalog:
    def __init__(self, db, cache, ttl=300, missing_ttl=30): ...
    @staticmethod
    def key(product_id) -> str: ...            # "product:v1:<id>"
    def get_product(self, product_id): ...     # dict, or None if the product does not exist
    def update_price(self, product_id, price_cents): ...
    def create_product(self, product_id, name, price_cents): ...
```

- `db` has `load(product_id)` (returns a dict or `None`, and counts a read), `update_price(product_id, price_cents)` and `create(product_id, name, price_cents)`.
- `cache` is a MiniRedis (same methods as `redis.Redis(decode_responses=True)`: `get`, `set(key, value, ex=...)`, `delete`, `ttl`).
- Store values as **JSON** (`json.dumps` / `json.loads`), never pickle.
- A product that exists is cached for `ttl` seconds. A product that does **not** exist is cached too, as the JSON text `null`, but only for `missing_ttl` seconds (negative caching).
- `update_price` changes the database **first**, then deletes the key.
- `create_product` creates the row, then deletes the key, so a cached "not found" does not hide the new product.

## Example

```python
catalog = Catalog(db, cache)
for _ in range(5):
    catalog.get_product(1)        # {'id': 1, 'name': 'Keyboard', 'price_cents': 4990}
db.reads                          # 1
catalog.get_product(99)           # None
catalog.get_product(99)           # None, from the cache
db.reads                          # 2
cache.get("product:v1:99")        # 'null'
cache.ttl("product:v1:99")        # 30
```

The tests give you `db` (a fake with a `reads` counter) and `cache` (MiniRedis on a fake clock).
