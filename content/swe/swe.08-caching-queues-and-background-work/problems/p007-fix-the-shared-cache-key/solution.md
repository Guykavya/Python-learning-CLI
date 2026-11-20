## Approach

The sequence: Asha (member) misses, the member price 4490 is stored under `price:1`; Ravi (public) asks, finds `price:1`, and gets 4490. The answer depends on `(product_id, tier)`, but the key only says `product_id`. Put the tier in the key:

```python
def price_for(cache, db, product_id, user):
    tier = user["tier"]
    key = f"price:{product_id}:{tier}"
    cached = cache.get(key)
    if cached is not None:
        return json.loads(cached)
    price = db.price(product_id, tier)
    cache.set(key, json.dumps(price), ex=PRICE_TTL)
    return price
```

Not the user's name: the price does not depend on who you are, only on your tier, so keying by name would give every public user a private copy (one database read per user instead of per tier) with no benefit. `product_info` does not depend on the user at all, so its shared key was already right.

## Cost

At most `products x tiers` cache entries (here 2 x 3). A key per user would be `products x users`: many more entries and a much lower hit ratio.

## Another way

Cache the tier-independent part (the base price) and compute the discount in code from the tier, so there is one entry per product. That works when the discount rule is cheap and lives in code. For HTTP caches, the equivalents are `Cache-Control: private` for personal responses and `Vary` for responses that depend on a header (chapter 4.4).
