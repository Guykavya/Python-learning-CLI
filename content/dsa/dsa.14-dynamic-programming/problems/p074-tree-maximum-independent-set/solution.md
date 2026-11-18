## Approach

Root the tree at node 0. The tree DP of section 18 has two values per node:

- `take(v)` = the largest independent set in the subtree of `v` that **contains** `v`: `1 + sum(skip(child))`, since the children are linked to `v`.
- `skip(v)` = the largest one that does **not** contain `v`: `sum(max(take(child), skip(child)))`, since each child is free.

The chapter computes them with a recursive post-order walk, which crashes on a path of 100,000 nodes. Any order in which **children come before parents** works, and the reverse of a BFS order is such an order. So: BFS once to get `order` and `parent`, then one backward pass that pushes each node's values into its parent.

```python
def max_independent_set(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    parent = [-1] * n
    seen = [False] * n
    seen[0] = True
    order = [0]
    i = 0
    while i < len(order):                       # BFS: every parent before its children
        v = order[i]
        i += 1
        for w in adj[v]:
            if not seen[w]:
                seen[w] = True
                parent[w] = v
                order.append(w)

    take = [1] * n                               # v itself
    skip = [0] * n
    for v in reversed(order):                    # children before parents
        p = parent[v]
        if p != -1:
            take[p] += skip[v]
            skip[p] += max(take[v], skip[v])
    return max(take[0], skip[0])
```

On the path `0-1-2-3-4`: node 4 is `(take 1, skip 0)`, node 3 `(1, 1)`, node 2 `(1 + 1, max(1, 1)) = (2, 1)`, node 1 `(1 + 1, 2) = (2, 2)`, node 0 `(1 + 2, 2) = (3, 2)`. Answer 3.

## Complexity

BFS and the backward pass each touch every node and edge once: `O(n)` time, `O(n)` memory, and no recursion at all.

## Another way

For a tree there is also a greedy that is provably right: repeatedly take a **leaf** into the set, and delete it together with its neighbour. (A leaf can always replace its neighbour in an optimal set: the exchange argument of dsa.13.) Implemented with a queue of current leaves and degree counts, it is also `O(n)`. The DP is more general: it works unchanged with weights on the nodes (house robber III on a general tree), where the leaf greedy fails.
