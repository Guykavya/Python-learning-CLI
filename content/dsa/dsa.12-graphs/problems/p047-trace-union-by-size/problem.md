# Trace union by size

This is the `DSU` class of chapter section 9 (union by size and path compression), with a `print` after every `union`. Predict **exactly** what the program prints. Do not run it.

```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, x):
        root = x
        while self.parent[root] != root:       # walk up to the root
            root = self.parent[root]
        while self.parent[x] != root:          # path compression
            nxt = self.parent[x]
            self.parent[x] = root
            x = nxt
        return root

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx                    # rx is the bigger root
        self.parent[ry] = rx
        self.size[rx] += self.size[ry]
        return True


d = DSU(7)
for x, y in [(0, 1), (2, 3), (3, 1), (4, 5), (5, 1), (6, 5), (0, 6)]:
    result = d.union(x, y)
    print(f"union({x}, {y}) -> {result}: parent={d.parent} size={d.size}")
```

Write your answer in `answer.txt`, one printed line per line (7 lines). Lists are printed the way Python prints them.

## How to work

Keep the two lists `parent` and `size` on paper, and draw the trees next to them. For every `union(x, y)`:

1. find the root of `x` and the root of `y` by following `parent` upwards. **Write down** which elements `find` passes: after it has found the root, it points every one of them **straight at the root** (path compression). That changes `parent` even if nothing is merged.
2. If the two roots are equal, nothing else changes and the result is `False`.
3. Otherwise compare the sizes **of the two roots**. When the sizes are **equal**, `rx` stays the root of `x` (the swap only happens when `rx`'s group is strictly smaller). The smaller root gets `parent = ` the bigger root; only the bigger root's `size` grows.

Notice that `size[i]` is never updated for an element that stops being a root.

## After you answer

1. After the last line, which entries of `size` are still meaningful, and which are left-over values?
2. Which `union` call changed an entry of `parent` through path compression, without that entry being one of the two roots?
3. The tallest tree in the final state has height 1 (every element points straight at the root). Would that be true without path compression? Draw the tree you would get.
