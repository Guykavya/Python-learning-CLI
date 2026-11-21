## Approach

```python
def position(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)


class Ring:
    def _rebuild(self):
        self.points = sorted((position(f"{n}#{i}"), n) for n in self.nodes for i in range(self.vnodes))
        self.positions = [p for p, _ in self.points]

    def node_for(self, key):
        if not self.points:
            raise ValueError("the ring is empty")
        return self.points[bisect.bisect(self.positions, position(key)) % len(self.points)][1]
```

This is the chapter's `Ring` (14.4) with `add` and `remove`. Measured with 10,000 keys: adding a 5th node moves about 19% of the keys with the ring (the ideal is 20%, only the new node's share) and about 80% with `hash % N`. **Virtual nodes** make the shares even: with one point per node the split is lumpy (the chapter: 640 / 272 / 8,034 / 11,054 keys), with 100 it is nearly equal. The same idea sits under Redis Cluster-like sharding, Cassandra, DynamoDB, memcached client libraries and CDNs.

## Complexity

`node_for` is O(log P) for P points (one binary search). `add` and `remove` rebuild the sorted list in O(P log P), which is fine because nodes change rarely; a production ring would insert the new points with `bisect.insort`.

## Another way

**Rendezvous (highest random weight) hashing**: for a key, score every node with `hash(node + key)` and pick the highest. No ring and no virtual nodes; the same minimal movement when nodes change, at the cost of O(N) per lookup.
