# Consistent hashing

Chapter section 14.4 (consistent hashing: spreading *data* so that adding a server moves little) and 15.4 (partitioning). A stateless app tier needs no memory of past requests, but when servers hold **data** (cache nodes, database shards), a key must always go to the same node. The obvious rule is `node = hash(key) % number_of_nodes`. It works until the number changes: going from 3 to 4 nodes remaps about **three quarters** of all keys. For a cache, three quarters of lookups suddenly miss and hit the database together (a stampede, swe.08).

A **hash ring** moves only about the new node's fair share. Nodes sit on a circle; each node gets many **virtual points** (so that the shares are even); a key belongs to the **next point clockwise**.

## What to write

```python
class Ring:
    def __init__(self, nodes=(), vnodes=100): ...
    def add(self, node): ...
    def remove(self, node): ...
    def node_for(self, key): ...
```

- The position of a thing on the ring is `int(hashlib.md5(text.encode()).hexdigest(), 16)`. Use **`hashlib.md5`, never `hash()`**: Python's `hash()` of a string is randomised **per process**, so two servers would disagree about who owns a key. (md5 is used for spreading, not for security.)
- Each node `n` puts `vnodes` points on the ring, at the positions of the texts `f"{n}#{i}"` for `i` in `range(vnodes)`.
- `node_for(key)` finds the first point whose position is **greater than** the position of `key` (going clockwise, wrapping from the last point to the first) and returns its node. Use `bisect`.
- `add(node)`: a node that is already on the ring raises `ValueError`. `remove(node)`: an unknown node raises `KeyError`. After either, the ring behaves exactly as if it had been built with the final set of nodes (the order in which nodes were added does not matter).
- `node_for` on an empty ring raises `ValueError`.
- The sorted points are kept in the attribute `points`, a list of `(position, node)` pairs (the tests look at its length: `vnodes` points per node).

## Example

```python
ring = Ring(["A", "B", "C"])
ring.node_for("user:1")                  # always the same node, in every process
ring.add("D")                            # only the keys that D takes over change owner (about a quarter)
ring.remove("D")                         # and they go back exactly to where they were
```

The tests count how many of 10,000 keys change node when a 5th node is added: with the ring about 20%; with `hash % n` about 80%.
