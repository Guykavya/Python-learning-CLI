# Build a graph library

Put the main tools of this module into one class. Write `class Graph` with:

| method | what it does |
|---|---|
| `Graph(n, directed=False)` | an empty graph with vertices `0 .. n-1` |
| `add_edge(u, v, w=1)` | add an edge `u -> v` of weight `w`; in an undirected graph also `v -> u`. A negative `w` raises `ValueError`; a vertex outside `0 .. n-1` raises `IndexError` |
| `bfs(s)` | the vertices reachable from `s`, in BFS order |
| `dfs(s)` | the vertices reachable from `s`, in DFS preorder, **without recursion** |
| `components()` | the connected components of an **undirected** graph: a list of sorted lists, ordered by their smallest vertex. On a directed graph raise `ValueError` |
| `topo()` | a topological order of a **directed** graph (a list of all `n` vertices), or `None` if there is a cycle. On an undirected graph raise `ValueError` |
| `shortest(s)` | Dijkstra: the list of distances from `s`, `float("inf")` for unreachable vertices |

The orders are pinned so the tests can compare them exactly:

- **Neighbours are visited in the order their edges were added.** For an undirected edge `(u, v)`, `v` is appended to the list of `u` and `u` to the list of `v`.
- `bfs` marks a vertex when it is **pushed**. `dfs` must give the same order as the recursive DFS (`visit(u)`: record `u`, then visit each unvisited neighbour in order): with a stack, push the neighbours in **reverse** and skip a vertex that is already visited when it is popped.
- Any valid topological order is accepted (the tests check it).

The tests use graphs with `10**5` vertices on a chain, so `dfs` (and `topo`, if you use DFS) must not recurse.

## Example

```python
>>> g = Graph(6)
>>> for u, v in [(0, 1), (0, 2), (1, 3), (2, 3), (4, 5)]:
...     g.add_edge(u, v)
>>> g.bfs(0)
[0, 1, 2, 3]
>>> g.dfs(0)
[0, 1, 3, 2]
>>> g.components()
[[0, 1, 2, 3], [4, 5]]
>>> d = Graph(3, directed=True)
>>> d.add_edge(0, 1, 5); d.add_edge(1, 2, 1); d.add_edge(0, 2, 9)
>>> d.shortest(0), d.topo()
([0, 5, 6], [0, 1, 2])
```

## Constraints

- `1 <= n <= 10**5`, up to `2 * 10**5` edges, weights `0 .. 10**6`. Every method `O(V + E)`, `shortest` `O((V + E) log V)`.

## Think about

Which methods need the edge weights and which ignore them? Why is `components` refused for a directed graph (what would "connected" even mean there)?
