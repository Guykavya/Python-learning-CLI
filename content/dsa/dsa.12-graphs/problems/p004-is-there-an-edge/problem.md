# Is there an edge?

A program asks two questions about a big graph, very often:

- "who are the neighbours of `u`?" (in edge-list order), and
- "is there an edge between `u` and `v`?".

Write a class `EdgeIndex`:

- `EdgeIndex(n, edges, directed=False)` stores the graph (vertices `0 .. n-1`).
- `neighbours(u)` returns a **list** of the neighbours of `u` in edge-list order (like `build_adj`, p001: a self loop once, parallel edges twice).
- `has_edge(u, v)` returns `True` or `False`. For an undirected graph `has_edge(u, v) == has_edge(v, u)`.

The catch: `has_edge` must be `O(1)` on average, even for a vertex with 100,000 neighbours, and the whole structure must use `O(n + E)` memory. The tests build a **star** (vertex 0 joined to 99,999 others) and ask 100,000 questions about vertex 0, in a separate process with a 10-second limit.

- Scanning `adj[u]` for `v` costs `O(degree)`: 100,000 questions times 100,000 neighbours is far too slow.
- An `n x n` matrix answers in `O(1)`, but for `n = 100,000` it has 10 billion cells: it does not fit in memory.

Chapter section 2 ("Which one?") names the structure that has both properties.

## Example

```python
>>> g = EdgeIndex(4, [(0, 1), (2, 0), (1, 2)])
>>> g.neighbours(0)
[1, 2]
>>> g.has_edge(0, 2), g.has_edge(2, 0), g.has_edge(0, 3)
(True, True, False)
>>> d = EdgeIndex(2, [(0, 1)], directed=True)
>>> d.has_edge(0, 1), d.has_edge(1, 0)
(True, False)
```

## Constraints

`1 <= n <= 10**5`, `0 <= len(edges) <= 2 * 10**5`. Building is `O(n + E)`; `has_edge` is `O(1)` average.
