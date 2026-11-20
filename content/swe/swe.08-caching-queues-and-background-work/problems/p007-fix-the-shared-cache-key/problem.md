# Fix the shared cache key

Chapter section 4.4 (the dangerous mistake: caching per-user data under a shared key). A shop shows prices that depend on the customer's **tier**: `public`, `member` or `staff`. Someone made the price lookup faster with a cache, and the code in `solution.py` works in every test they wrote, all of which used one user. In production, **Ravi (public) sometimes sees Asha's member price**, and staff discounts leak to everybody.

```python
def price_for(cache, db, product_id, user):
    key = f"price:{product_id}"
    ...

def product_info(cache, db, product_id):
    key = f"info:{product_id}"
    ...
```

`user` is a dict such as `{"name": "asha", "tier": "member"}`. `db.price(product_id, tier)` and `db.info(product_id)` are the slow queries.

## Your task

1. Find out why Ravi sees Asha's price. Write the two-user sequence that shows it.
2. Fix `price_for` so each tier gets its own price. Keep the cache **shared by everyone in the same tier**: two public users must share one cache entry (one database read), because the price does not depend on *who* they are, only on their tier.
3. Do not change `product_info`: product names are the same for everybody, so one shared key is correct there.

Keep the TTLs and the JSON format as they are.

## Example

```python
asha = {"name": "asha", "tier": "member"}
ravi = {"name": "ravi", "tier": "public"}
price_for(cache, db, 1, asha)    # 4490
price_for(cache, db, 1, ravi)    # buggy: 4490 (Asha's!)   fixed: 4990
```

The tests alternate users and tiers. They also check that the cache is still shared where it should be.
