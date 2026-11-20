## Approach

Chapter section 3. Position `i` lies in exactly one node per level: the path from the root to its leaf. Walk down that path, set the leaf, and **recompute every node on the way back up** from its two children.

```python
    def update(self, i, v):
        self._update(1, 0, self.n, i, v)

    def _update(self, node, lo, hi, i, v):
        if hi - lo == 1:                       # the leaf of position i
            self.t[node] = v
            return
        mid = (lo + hi) // 2
        if i < mid:
            self._update(2 * node, lo, mid, i, v)
        else:
            self._update(2 * node + 1, mid, hi, i, v)
        self.t[node] = self.t[2 * node] + self.t[2 * node + 1]   # fix on the way back up
```

The build and the query are those of p002. In the example, the path of `a[3]` is node 11 (the leaf), 5 (`[2,4)`), 2 (`[0,4)`) and 1 (the root): exactly the four entries that change.

## Complexity

`O(log n)` per update (one node per level), `O(log n)` per query, `O(n)` build, `4n` memory.

## Another way

Set the leaf, then add the difference `v - old` to every node on the path (no recomputation from children). It works for sums, but not for min, max or gcd, where the parent cannot be fixed from a difference. Recomputing from the children works for every operation.
