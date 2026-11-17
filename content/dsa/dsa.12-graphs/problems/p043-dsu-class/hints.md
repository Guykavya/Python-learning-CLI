## Hint 1

Keep two lists: `parent[x]` (the root points to itself) and `size[r]` (only meaningful for roots). Also keep a counter of groups. Which of these change in `union`, and only when?

## Hint 2

`find(x)`: first walk up with `while parent[root] != root` to find the root; then walk from `x` again and set each `parent` on the way to the root. `union(x, y)`: `rx, ry = find(x), find(y)`; if equal return `False`; otherwise make `rx` the bigger root, set `parent[ry] = rx`, `size[rx] += size[ry]`, lower the counter, return `True`.

## Hint 3

```
def find(self, x):
    root = x
    while self.parent[root] != root: root = self.parent[root]
    while self.parent[x] != root:
        nxt = self.parent[x]; self.parent[x] = root; x = nxt
    return root

def union(self, x, y):
    rx, ry = self.find(x), self.find(y)
    if rx == ry: return False
    if self.sz[rx] < self.sz[ry]: rx, ry = ry, rx
    self.parent[ry] = rx; self.sz[rx] += self.sz[ry]; self.groups -= 1
    return True
```

Careful: if you store the sizes in an attribute called `size`, it hides the method `size(x)`. Use another name such as `sz`.
