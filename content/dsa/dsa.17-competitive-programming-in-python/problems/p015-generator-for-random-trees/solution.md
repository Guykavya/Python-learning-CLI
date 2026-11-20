## Approach

```python
def random_tree(n, rng, shape="random"):
    if shape not in ("random", "path", "star"):
        raise ValueError(f"unknown shape: {shape}")
    if n == 1:
        return []
    parent = [0] * n
    for i in range(1, n):
        if shape == "random":
            parent[i] = rng.randrange(i)
        elif shape == "path":
            parent[i] = i - 1
        else:
            parent[i] = 0
    perm = list(range(1, n + 1))
    rng.shuffle(perm)
    edges = []
    for i in range(1, n):
        u, v = perm[parent[i]], perm[i]
        if rng.random() < 0.5:
            u, v = v, u
        edges.append((u, v))
    rng.shuffle(edges)
    return edges
```

Why it is a tree: every position `i >= 1` has exactly one edge to an earlier position, so there are `n - 1` edges and every vertex connects down to position 0. A connected graph with `n - 1` edges has no cycle. The permutation and the swaps only rename and reorder, so they keep the tree and remove the "parent is smaller" pattern.

Example: `n = 3`, shape `"path"`: positions give edges `(0,1)`, `(1,2)`; a permutation such as `[2, 3, 1]` turns them into `(2, 3)`, `(3, 1)`.

## Complexity

`O(n)`.

## Another way

Generate a random **Prüfer sequence** of length `n - 2` and decode it: every labelled tree appears with equal probability. The random-attach method is simpler but favours some shapes (it produces shallow trees on average), which is why the `"path"` and `"star"` shapes exist.
