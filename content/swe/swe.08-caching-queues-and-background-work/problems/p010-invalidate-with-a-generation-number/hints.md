## Hint 1

In p009 the stale value came from a reader that read the database *before* the write and stored *after* it. With generations, what decides **where** the reader's store lands? When must the reader learn the generation so that a late store is harmless?

## Hint 2

```text
read_product(cache, load, id, ttl):
    gen = current_gen(cache, id)                 # 1. first
    raw = cache.get(value_key(id, gen))          # 2.
    if raw is not None: return json.loads(raw)
    product = load(id)                           # 3.
    cache.set(value_key(id, gen), json.dumps(product), ex=ttl)   # same gen as step 1
    return product

invalidate(cache, id): return cache.incr(gen_key(id))
```

Writer order: update the database, **then** `invalidate`. A reader that read generation 0 before the bump stores into `g0`; every later reader looks in `g1`.
