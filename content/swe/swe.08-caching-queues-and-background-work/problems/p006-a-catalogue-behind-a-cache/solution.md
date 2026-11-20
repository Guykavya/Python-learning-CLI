## Approach

Cache-aside: the application talks to the cache and the database itself. JSON turns "not found" into the text `null`, which is different from a cache miss (`None` from `get`), so negative caching needs no special marker.

```python
import json


class Catalog:
    def __init__(self, db, cache, ttl=300, missing_ttl=30):
        self.db, self.cache, self.ttl, self.missing_ttl = db, cache, ttl, missing_ttl

    @staticmethod
    def key(product_id):
        return f"product:v1:{product_id}"

    def get_product(self, product_id):
        cached = self.cache.get(self.key(product_id))
        if cached is not None:
            return json.loads(cached)
        product = self.db.load(product_id)
        ttl = self.ttl if product is not None else self.missing_ttl
        self.cache.set(self.key(product_id), json.dumps(product), ex=ttl)
        return product

    def update_price(self, product_id, price_cents):
        self.db.update_price(product_id, price_cents)
        self.cache.delete(self.key(product_id))

    def create_product(self, product_id, name, price_cents):
        self.db.create(product_id, name, price_cents)
        self.cache.delete(self.key(product_id))
```

## Cost

A hit costs one cache round trip; a miss costs a cache lookup, a database read and a cache write. With a 90% hit ratio, 9 of 10 requests never reach the database. Negative caching protects the database from requests for ids that do not exist (typos, scanners): one read per 30 seconds per bad id instead of one per request.

## Another way

**Write-through:** `update_price` stores the new product in the cache instead of deleting it. Readers never see a miss after a write, but two writers can race and leave the older value in the cache (chapter 5.3), so deletion plus a TTL is the safer default. Problem p010 shows a generation number that removes the read/write race entirely.
