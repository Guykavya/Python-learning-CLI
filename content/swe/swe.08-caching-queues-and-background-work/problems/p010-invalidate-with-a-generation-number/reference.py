import json


def gen_key(product_id):
    return f"product:{product_id}:gen"


def value_key(product_id, gen):
    return f"product:{product_id}:g{gen}"


def current_gen(cache, product_id):
    return int(cache.get(gen_key(product_id)) or 0)


def read_product(cache, load, product_id, ttl=300):
    gen = current_gen(cache, product_id)                  # FIRST: which generation am I serving?
    key = value_key(product_id, gen)
    cached = cache.get(key)
    if cached is not None:
        return json.loads(cached)
    product = load(product_id)
    cache.set(key, json.dumps(product), ex=ttl)          # a late store lands in a generation nobody reads
    return product


def invalidate(cache, product_id):
    return cache.incr(gen_key(product_id))
