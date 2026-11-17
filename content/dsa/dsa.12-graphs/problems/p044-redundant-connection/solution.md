## Approach

The graph is a tree plus one edge, so it has exactly one cycle, and removing any edge of that cycle leaves a tree. Among those we want the one that comes last in the list.

Add the edges in list order with Union-Find (chapter section 9). Two ends already in the same group means a path between them exists through edges added **before**, so this edge closes a cycle. The first time that happens, all the other edges of the one cycle are already in, so this edge is the cycle's **last** edge in the list: exactly what is asked. No search is needed, and the edges after it do not matter.

```python
def redundant_edge(n, edges):
    parent = list(range(n))
    size = [1] * n

    def find(x):
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            return (u, v)                          # u and v were already connected
        if size[ru] < size[rv]:
            ru, rv = rv, ru
        parent[rv] = ru
        size[ru] += size[rv]
    return None                                    # not reached for valid input
```

The line `parent[x], x = root, parent[x]` first computes the right side (`root` and the **old** `parent[x]`), then assigns: it points `x` at the root and moves on to its old parent.

## Complexity

Nearly `O(n)`: `n` unions and finds, each amortised almost constant.

## Another way

Find the cycle with a DFS (chapter section 6) and collect its edges; then return the cycle edge with the largest index in the list. It is `O(n)` too but needs more code. The brute force (remove each edge from the last to the first and check whether a tree remains) is `O(n^2)`.
