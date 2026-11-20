# Delete-after-write is not enough

Chapter section 5.2 (the classic race). A **reader** misses the cache, reads the database, then stores what it read. A **writer** updates the database, then deletes the cache key. The program below runs **every** interleaving of the two step lists (each list keeps its own order) and reports what is left in the cache and what a later reader would see.

```python
from itertools import combinations

from miniredis import MiniRedis        # the chapter's MiniRedis (section 3.2)


def interleavings(a, b):
    """Every way to merge two step lists, keeping the order inside each list."""
    n = len(a) + len(b)
    for positions in combinations(range(n), len(a)):
        merged, ia, ib = [], iter(a), iter(b)
        for i in range(n):
            merged.append(next(ia) if i in positions else next(ib))
        yield merged


def r_read_db(w): w["local"]["v"] = w["db"]
def r_store(w): w["cache"].set("p", w["local"]["v"])
def w_update(w): w["db"] = "NEW"
def w_delete(w): w["cache"].delete("p")


stale = 0
for number, order in enumerate(interleavings([r_read_db, r_store], [w_update, w_delete]), start=1):
    world = {"db": "OLD", "cache": MiniRedis(), "local": {}}
    for step in order:
        step(world)
    cached = world["cache"].get("p")
    fresh = cached or world["db"]                 # a later reader: cache first, database on a miss
    if fresh != "NEW":
        stale += 1
    print(f"{number}: cache={cached} read={fresh}")
print(f"stale: {stale}")
```

Facts you need: `combinations(range(4), 2)` yields the reader's positions in this order: `(0, 1)`, `(0, 2)`, `(0, 3)`, `(1, 2)`, `(1, 3)`, `(2, 3)`. Position numbers not used by the reader are filled with the writer's steps in their order. MiniRedis `get` returns `None` for a missing key; `delete` of a missing key does nothing.

## What to write

Write the exact output: seven lines.

## Example

The first interleaving is `r_read_db, r_store, w_update, w_delete`. The reader stores `OLD`, the writer deletes it, so the cache is empty and a later read goes to the database, which says `NEW`. Its line is `1: cache=None read=NEW`.

## After you answer

- Write the stale order as a two-lane timeline (reader lane, writer lane).
- Would swapping the writer's steps (delete first, then update) make it better or worse? Try it: change the list and run.
