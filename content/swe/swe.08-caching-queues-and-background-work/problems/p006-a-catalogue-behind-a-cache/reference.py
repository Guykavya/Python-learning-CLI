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
            return json.loads(cached)             # may be None: a cached "not found"
        product = self.db.load(product_id)
        ttl = self.ttl if product is not None else self.missing_ttl
        self.cache.set(self.key(product_id), json.dumps(product), ex=ttl)
        return product

    def update_price(self, product_id, price_cents):
        self.db.update_price(product_id, price_cents)   # the source of truth first
        self.cache.delete(self.key(product_id))         # then invalidate

    def create_product(self, product_id, name, price_cents):
        self.db.create(product_id, name, price_cents)
        self.cache.delete(self.key(product_id))         # drop a cached "not found"
