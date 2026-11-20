## Approach

Every group is a tree whose root is the representative (chapter section 9). `find` walks up to the root; `union` links one root under the other. The two tricks keep the trees flat:

- **Union by size** puts the smaller tree under the bigger root, so an element sinks one level only when its group at least doubles: no tree is taller than `log2 n`.
- **Path compression** makes every element visited by `find` point straight at the root.

Together the cost per operation is "nearly constant" (the inverse Ackermann function, below 5 for any real `n`; see p049).

Sizes live in the list `sz` and are correct for roots only; `size(x)` therefore asks for the size of `find(x)`. The group counter drops by one exactly when `union` merges two different groups.

```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.sz = [1] * n                          # valid for roots only
        self.groups = n

    def find(self, x):
        root = x
        while self.parent[root] != root:           # walk up to the root
            root = self.parent[root]
        while self.parent[x] != root:              # path compression
            nxt = self.parent[x]
            self.parent[x] = root
            x = nxt
        return root

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.sz[rx] < self.sz[ry]:
            rx, ry = ry, rx                        # rx is the bigger root
        self.parent[ry] = rx
        self.sz[rx] += self.sz[ry]
        self.groups -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)

    def count(self):
        return self.groups

    def size(self, x):
        return self.sz[self.find(x)]
```

## Complexity

`O(n)` to build. Every operation is amortised `O(alpha(n))`, practically `O(1)`.

## Another way

Union by **rank** (an upper bound on the height) instead of size gives the same guarantee. **Path halving** is a one-loop alternative to full compression: `while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]` makes every other element on the path skip a level. A recursive `find` with compression is the shortest code, but on a long path built before any compression it passes the recursion limit.
