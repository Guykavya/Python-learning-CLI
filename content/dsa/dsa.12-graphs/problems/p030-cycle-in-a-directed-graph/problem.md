# Cycle in a directed graph

Write `has_cycle_directed(n, edges)`. The graph is **directed**: an edge `(u, v)` goes from `u` to `v` only. Vertices are `0 .. n-1`. Return `True` if there is a directed cycle (a way to follow edges from some vertex back to itself), `False` otherwise.

"I have seen this vertex before" is **not** a cycle in a directed graph: in a diamond `0 -> 1 -> 3`, `0 -> 2 -> 3`, vertex 3 is reached twice, but you can never come back to where you started. Use the **three colours** of chapter section 6:

- WHITE: not visited yet;
- GREY: on the current path of the DFS (entered, not finished);
- BLACK: finished, everything below it was explored and no cycle was found through it.

An edge to a **GREY** vertex goes back to a vertex on the current path: that is a cycle. An edge to a BLACK vertex is harmless.

## Example

```python
>>> has_cycle_directed(4, [(0, 1), (0, 2), (1, 3), (2, 3)])   # a diamond
False
>>> has_cycle_directed(3, [(0, 1), (1, 2), (2, 0)])           # a loop
True
>>> has_cycle_directed(2, [(1, 1)])                           # a self loop
True
>>> has_cycle_directed(3, [(0, 1), (1, 0)])                   # 0 -> 1 -> 0
True
```

## Constraints

- `1 <= n <= 10**5`, `0 <= len(edges) <= 2 * 10**5`.
- A chain of 100,000 vertices is in the tests, so the DFS must use an **explicit stack** (chapter section 7 shows a DFS that keeps an iterator per vertex on the stack). A recursive DFS gets a `RecursionError`.

## Think about

Why is a BLACK vertex safe to meet again? What would go wrong if you reset a vertex to WHITE when you leave it, instead of making it BLACK?
