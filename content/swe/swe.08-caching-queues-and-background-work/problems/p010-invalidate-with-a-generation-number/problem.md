# Invalidate with a generation number

Chapter sections 5.2 (scheme 2: a generation key) and 5.3 (versioned keys). Problem p009 showed that "update the database, then delete the key" can leave a stale value. The fix from the chapter: each product has a **generation number** in Redis. The cached value lives under a key that **contains** the generation. A writer updates the database and then **increments** the generation. A slow reader that read the old generation stores its old value under the **old** key, which nobody reads any more.

## What to write

```python
def gen_key(product_id) -> str: ...                  # "product:<id>:gen"
def value_key(product_id, gen: int) -> str: ...      # "product:<id>:g<gen>"
def current_gen(cache, product_id) -> int: ...       # 0 when the generation key does not exist yet
def read_product(cache, load, product_id, ttl=300): ...
def invalidate(cache, product_id) -> int: ...        # the new generation
```

- `read_product` reads the generation **first**, then looks in the cache under `value_key(id, gen)`. On a miss it calls `load(product_id)` (the database) and stores the JSON under the key **of the generation it read at the start**, with `ex=ttl`. It returns the product (a dict).
- `invalidate` bumps the generation with **one** `INCR` (atomic, so two writers never get the same number). It does not delete anything: old entries are never read again and disappear by their TTL.
- The generation key itself has no expiry.

## Example

```python
read_product(cache, load, 1)       # miss: loads, stores under 'product:1:g0'
read_product(cache, load, 1)       # hit
invalidate(cache, 1)               # 1   (the writer has already updated the database)
read_product(cache, load, 1)       # miss under 'product:1:g1': loads the new data
cache.ttl("product:1:g0")          # still positive: the old entry simply expires later
```

The tests replay every interleaving of a reader (read generation, load, store) and a writer (update the database, invalidate) and check that a later read always sees the new data. They build the reader's three steps from your `current_gen` and `value_key`, so those must follow the rules above.
