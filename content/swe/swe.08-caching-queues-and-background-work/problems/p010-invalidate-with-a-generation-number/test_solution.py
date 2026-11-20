import json
from itertools import combinations

from solution import current_gen, gen_key, invalidate, read_product, value_key


class DB:
    def __init__(self):
        self.price = "OLD"
        self.loads = 0

    def load(self, product_id):
        self.loads += 1
        return {"id": product_id, "price": self.price}


def test_key_formats():
    assert gen_key(7) == "product:7:gen", "Generation key: 'product:<id>:gen'."
    assert value_key(7, 3) == "product:7:g3", "Value key: 'product:<id>:g<gen>'."


def test_current_gen_defaults_to_zero(r):
    assert current_gen(r, 1) == 0, "No generation key yet means generation 0."
    r.set("product:1:gen", "4")
    assert current_gen(r, 1) == 4, "current_gen must return an int (Redis stores strings)."


def test_hit_after_miss(r):
    db = DB()
    first = read_product(r, db.load, 1)
    second = read_product(r, db.load, 1)
    assert first == second == {"id": 1, "price": "OLD"}
    assert db.loads == 1, "The second read must be a cache hit."
    assert json.loads(r.get("product:1:g0")) == first, "The value is stored as JSON under the generation-0 key."
    assert r.ttl("product:1:g0") == 300, "Store with ex=ttl (300 by default)."


def test_invalidate_bumps_and_reloads(r):
    db = DB()
    read_product(r, db.load, 1)
    db.price = "NEW"
    assert invalidate(r, 1) == 1, "invalidate returns the new generation (INCR's result)."
    assert read_product(r, db.load, 1)["price"] == "NEW", "After invalidate the next read must load the new data."
    assert db.loads == 2
    assert invalidate(r, 1) == 2


def test_invalidate_does_not_delete(r, clock):
    db = DB()
    read_product(r, db.load, 1)
    invalidate(r, 1)
    assert r.get("product:1:g0") is not None, "invalidate must not delete old entries: they are simply never read again."
    assert r.ttl("product:1:gen") == -1, "The generation key has no expiry; otherwise generations could go back to 0."
    clock.advance(300)
    assert r.get("product:1:g0") is None, "Old entries disappear by their TTL."


def test_products_are_independent(r):
    db = DB()
    read_product(r, db.load, 1)
    read_product(r, db.load, 2)
    invalidate(r, 1)
    read_product(r, db.load, 2)
    assert db.loads == 2, "Invalidating product 1 must not affect product 2's cache."


def _interleavings(a, b):
    n = len(a) + len(b)
    for positions in combinations(range(n), len(a)):
        merged, ia, ib = [], iter(a), iter(b)
        for i in range(n):
            merged.append(next(ia) if i in positions else next(ib))
        yield merged


def test_no_interleaving_leaves_stale_data(make_redis):
    def r_read_gen(w): w["gen"] = current_gen(w["cache"], 1)
    def r_load(w): w["v"] = {"id": 1, "price": w["db"]}
    def r_store(w): w["cache"].set(value_key(1, w["gen"]), json.dumps(w["v"]), ex=300)
    def w_update(w): w["db"] = "NEW"
    def w_invalidate(w): invalidate(w["cache"], 1)

    stale = []
    for order in _interleavings([r_read_gen, r_load, r_store], [w_update, w_invalidate]):
        world = {"db": "OLD", "cache": make_redis()}
        for step in order:
            step(world)
        seen = read_product(world["cache"], lambda pid: {"id": pid, "price": world["db"]}, 1)["price"]
        if seen != "NEW":
            stale.append([s.__name__ for s in order])
    assert not stale, f"These interleavings leave a stale value: {stale}. Read the generation FIRST and store under that generation's key."
