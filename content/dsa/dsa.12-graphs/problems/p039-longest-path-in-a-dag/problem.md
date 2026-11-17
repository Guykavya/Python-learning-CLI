# Longest path in a DAG

The graph is a **DAG** (directed, no cycles; the tests only give DAGs) with vertices `0 .. n-1` and weighted edges `(u, v, w)`: an edge from `u` to `v` with weight `w` (an integer, possibly negative). The same pair `u, v` can have several edges.

Write two functions (chapter section 7, "Dynamic programming on a DAG"):

1. `longest_from(n, edges, source)` returns a list `best` of length `n`: `best[v]` is the **largest** total weight of a path from `source` to `v`, and `None` if no path goes from `source` to `v`. `best[source]` is `0` (the empty path).
2. `count_paths(n, edges, source, target)` returns the **number of different paths** from `source` to `target`, modulo `10**9 + 7`. Two paths are different if they use a different sequence of **edges**, so parallel edges count separately. If `source == target` the answer is `1` (the empty path). The weights do not matter here.

Both are filled in **topological order**: when you reach `v`, every `u` with an edge `u -> v` is already final.

- `best[v] = max(best[u] + w)` over the edges `u -> v` with `best[u]` not `None`;
- `ways[v] = sum(ways[u])` over the edges `u -> v`, with `ways[source] = 1`.

## Example

```python
>>> edges = [(0, 1, 2), (0, 2, 5), (1, 2, 4), (2, 3, 1), (1, 3, 1), (4, 3, 10)]
>>> longest_from(5, edges, 0)
[0, 2, 6, 7, None]
>>> count_paths(5, edges, 0, 3)        # 0-1-2-3, 0-2-3, 0-1-3
3
>>> count_paths(3, [(0, 1, 1), (0, 1, 7), (1, 2, 0)], 0, 2)   # two parallel edges 0 -> 1
2
```

`best[2] = 6` uses `0 -> 1 -> 2` (2 + 4), which beats the direct edge of weight 5. Vertex 4 cannot be reached from 0, so `best[4]` is `None`, and its edge into 3 must **not** count (`best[3]` is 7, not 10).

## Constraints

- `1 <= n <= 10**5`, `0 <= len(edges) <= 2 * 10**5`, `-10**4 <= w <= 10**4`. `O(n + E)` time, no recursion.
- The number of paths can be astronomically large (a chain of doubled edges has `2**(n-1)` paths): take every sum modulo `10**9 + 7`.

## Think about

Why is the longest path easy in a DAG but hard in a general graph? What does the topological order guarantee that a plain loop over `0, 1, 2, ...` does not?
