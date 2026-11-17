# Shortest path itself

Knowing that the distance is 4 is often not enough: a navigation app must show the **route**. BFS can remember, for every vertex, the vertex that discovered it (its **parent**). Walking back from `t` through the parents and reversing gives a shortest path (chapter section 3, "Getting the path back").

Write `shortest_path(n, edges, s, t)` for an **undirected** graph with vertices `0 .. n-1`. It returns a list of vertices `[s, ..., t]`:

- consecutive vertices are joined by an edge;
- the number of edges (`len(path) - 1`) is the smallest possible;
- `[s]` if `s == t`;
- `None` if `t` cannot be reached.

When several shortest paths exist, **any** of them is accepted: the tests check the three rules above instead of comparing with one fixed path.

## Example

```python
>>> shortest_path(5, [(0, 1), (1, 2), (2, 3), (0, 3)], 0, 2)
[0, 1, 2]                      # [0, 3, 2] is accepted too
>>> shortest_path(5, [(0, 1)], 0, 4)
None
>>> shortest_path(2, [], 1, 1)
[1]
```

## Constraints

`1 <= n <= 10**5`, up to `2 * 10**5` edges. `O(n + E)` time; the tests use a path of 100,000 vertices.
