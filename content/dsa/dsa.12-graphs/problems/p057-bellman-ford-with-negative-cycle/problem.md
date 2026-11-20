# Bellman-Ford with negative cycles

Write `bellman_ford(n, edges, source)`. The graph has vertices `0 .. n-1` and **directed** edges `(u, v, w)`; weights **may be negative**.

- If a **negative cycle** (a cycle whose weights add up to less than 0) can be **reached from `source`**, return `None`: some shortest distances do not exist.
- Otherwise return the list of shortest distances from `source`, with `float("inf")` for vertices that cannot be reached.

A negative cycle that **cannot be reached** from the source does not matter: return the normal distances.

This is chapter section 12: `V - 1` rounds that relax every edge, then one more round. If that extra round can still improve a distance, there is a negative cycle reachable from the source.

## Example

```python
>>> bellman_ford(4, [(0, 1, 4), (0, 2, 5), (2, 1, -3), (1, 3, 2)], 0)
[0, 2, 5, 4]
>>> bellman_ford(3, [(0, 1, 1), (1, 2, -2), (2, 1, 1)], 0) is None
True
>>> bellman_ford(4, [(0, 1, 3), (2, 3, -5), (3, 2, 1)], 0)
[0, 3, inf, inf]
```

In the second example `1 -> 2 -> 1` adds up to `-1` and is reachable from 0. In the third, `2 -> 3 -> 2` is negative too, but 0 cannot reach it.

## Constraints

- `1 <= n <= 300`, `0 <= len(edges) <= 3000`, `-1000 <= w <= 1000`. `O(V * E)` time.
- Do not change `edges`.

## Think about

Why exactly `V - 1` rounds? Why does a vertex with distance `inf` never "improve" through a negative edge, and why does that make unreachable cycles harmless?
