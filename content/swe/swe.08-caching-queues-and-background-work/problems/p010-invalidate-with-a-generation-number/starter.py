import json


def gen_key(product_id):
    return f"product:{product_id}:gen"


def value_key(product_id, gen):
    # TODO
    return f"product:{product_id}"


def current_gen(cache, product_id):
    # TODO: int of the generation key, 0 if missing
    return 0


def read_product(cache, load, product_id, ttl=300):
    # TODO: generation first, then the value under that generation's key
    return load(product_id)


def invalidate(cache, product_id):
    # TODO: one INCR
    return 0
