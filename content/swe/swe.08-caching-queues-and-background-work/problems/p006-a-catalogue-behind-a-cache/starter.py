import json


class Catalog:
    def __init__(self, db, cache, ttl=300, missing_ttl=30):
        self.db, self.cache, self.ttl, self.missing_ttl = db, cache, ttl, missing_ttl

    @staticmethod
    def key(product_id):
        return f"product:v1:{product_id}"

    def get_product(self, product_id):
        # TODO: cache first; on a miss load, store as JSON (null for "not found", shorter ttl)
        return self.db.load(product_id)

    def update_price(self, product_id, price_cents):
        # TODO: database first, then invalidate
        self.db.update_price(product_id, price_cents)

    def create_product(self, product_id, name, price_cents):
        # TODO
        self.db.create(product_id, name, price_cents)
