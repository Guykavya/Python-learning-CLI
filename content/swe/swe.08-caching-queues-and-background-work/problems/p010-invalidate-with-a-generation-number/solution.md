## Approach

The generation number turns "invalidate" into "move everybody to a new key". The reader decides its key **before** it reads the database, so a reader that saw old data can only write into an old generation.

```python
import json


def gen_key(product_id):
    return f"product:{product_id}:gen"


def value_key(product_id, gen):
    return f"product:{product_id}:g{gen}"


def current_gen(cache, product_id):
    return int(cache.get(gen_key(product_id)) or 0)


def read_product(cache, load, product_id, ttl=300):
    gen = current_gen(cache, product_id)
    key = value_key(product_id, gen)
    cached = cache.get(key)
    if cached is not None:
        return json.loads(cached)
    product = load(product_id)
    cache.set(key, json.dumps(product), ex=ttl)
    return product


def invalidate(cache, product_id):
    return cache.incr(gen_key(product_id))
```

Why every interleaving is safe: if the reader reads the generation **after** the bump, it also reads the database after the update (the writer updated first), so it stores NEW under the new key. If it reads the generation **before** the bump, whatever it stores goes under the old key, which no later reader looks at. The test checks all 10 interleavings.

## Cost

A read costs two cache round trips (generation, then value) instead of one. Each write leaves one orphaned entry that lives until its TTL, so memory use grows with the write rate times the TTL.

## Another way

Store a version number inside the cached value and accept an update only if it is newer (compare-and-set). Real Redis needs a Lua script or `WATCH` for that. Two round trips can also be reduced to one with `MGET`-style tricks, or by keeping the generation in a small in-process cache for a second.
