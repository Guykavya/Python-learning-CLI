## Hint 1

`cache.get` returns `None` for a miss. If you also store "not found" as `None`, how would you tell "not in the cache" from "cached as missing"? What does `json.dumps(None)` give?

## Hint 2

```text
get_product(id):
    raw = cache.get(key(id))
    if raw is not None: return json.loads(raw)        # "null" -> None: a cached not-found
    product = db.load(id)
    cache.set(key(id), json.dumps(product), ex = ttl if product else missing_ttl)
    return product

update_price(id, cents): db.update_price(id, cents); cache.delete(key(id))
create_product(...):     db.create(...);             cache.delete(key(id))
```
