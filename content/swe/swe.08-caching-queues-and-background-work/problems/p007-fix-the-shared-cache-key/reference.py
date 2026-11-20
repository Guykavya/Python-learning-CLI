import json

PRICE_TTL = 60
INFO_TTL = 3600


def price_for(cache, db, product_id, user):
    """The price this user pays, in cents."""
    tier = user["tier"]
    key = f"price:{product_id}:{tier}"          # everything the answer depends on is in the key
    cached = cache.get(key)
    if cached is not None:
        return json.loads(cached)
    price = db.price(product_id, tier)
    cache.set(key, json.dumps(price), ex=PRICE_TTL)
    return price


def product_info(cache, db, product_id):
    """Name and id: the same for everybody."""
    key = f"info:{product_id}"
    cached = cache.get(key)
    if cached is not None:
        return json.loads(cached)
    info = db.info(product_id)
    cache.set(key, json.dumps(info), ex=INFO_TTL)
    return info
