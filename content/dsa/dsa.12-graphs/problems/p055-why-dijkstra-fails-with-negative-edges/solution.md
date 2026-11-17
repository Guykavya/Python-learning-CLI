## Approach

Find the step of the proof that uses non-negative weights, then build the smallest graph that breaks exactly that step: a vertex settled through a cheap direct edge, and a route through a more expensive vertex that a negative edge makes cheaper.

## Code

```python
edges = [(0, 1, 1), (0, 2, 3), (2, 1, -3)]
print(dijkstra_done_set(3, edges, 0))   # [0, 1, 3]  wrong for vertex 1
print(bellman_ford(3, edges, 0))        # [0, 0, 3]  right
```

## Complexity

Bellman-Ford, the fix, costs `O(V * E)` time and `O(V)` memory, against `O((V + E) log V)` for Dijkstra.

## Another way

If the negative weights come from a known potential (for example in Johnson's algorithm), you can **re-weight** every edge `w(u, v) + h(u) - h(v)` with values `h` from one Bellman-Ford run. This shift is different for every edge and changes every route between the same two vertices by the same amount `h(start) - h(end)`, which is why it works where a constant shift fails.
