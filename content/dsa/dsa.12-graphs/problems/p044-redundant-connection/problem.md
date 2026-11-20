# Redundant connection

A network started as a **tree** on the vertices `0 .. n-1` (connected, `n - 1` undirected edges, no cycle). Then **one** extra edge was added between two different vertices that were not yet directly joined. You get all `n` edges in a list `edges`, in some order.

Write `redundant_edge(n, edges)`. Return an edge that can be removed so that the remaining `n - 1` edges form a tree again. Several edges may work (any edge of the one cycle); return the one that appears **last** in `edges`. Return it as a tuple, exactly as it is written in the list (do not swap its two ends).

Union-Find (chapter section 9) does this in one pass: go through the edges in order and unite their ends; the first edge whose two ends are **already** in the same group closes the cycle.

## Example

```python
>>> redundant_edge(3, [(0, 1), (0, 2), (1, 2)])
(1, 2)
>>> redundant_edge(5, [(0, 1), (1, 2), (2, 3), (1, 3), (0, 4)])
(1, 3)
>>> redundant_edge(4, [(2, 1), (3, 1), (2, 3), (0, 3)])
(2, 3)
```

## Constraints

- `3 <= n <= 10**5`, `len(edges) == n`. Nearly `O(n)` time.

## Think about

The rule says "the cycle edge that appears **last**". Why is the first edge that Union-Find rejects exactly that edge, and not just any edge of the cycle?
