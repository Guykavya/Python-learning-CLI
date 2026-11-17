# Topological order (Kahn)

A directed edge `(u, v)` means "`u` must come before `v`". Write `topo_kahn(n, edges)` for vertices `0 .. n-1`. It returns a list of all `n` vertices in an order where, for **every** edge `(u, v)`, `u` comes before `v` (a **topological order**). If no such order exists (the graph has a cycle), return the empty list `[]`.

Use **Kahn's algorithm** (chapter section 7):

1. count the **in-degree** of every vertex (how many edges point to it);
2. put every vertex with in-degree 0 in a queue (nothing has to come before it);
3. repeatedly take a vertex out, append it to the order, and "remove" its outgoing edges: lower the in-degree of each target, and when a target drops to 0, put it in the queue;
4. if the order has fewer than `n` vertices at the end, the rest are stuck on or behind a cycle.

Usually many orders are correct. The tests **check** your order (every vertex once, every edge respected); any valid order is accepted.

Rules: the same edge can be listed twice (count both); a self loop `(u, u)` is a cycle.

## Example

```python
>>> topo_kahn(4, [(0, 1), (0, 2), (1, 3), (2, 3)])
[0, 1, 2, 3]                  # [0, 2, 1, 3] is also correct
>>> topo_kahn(3, [(0, 1), (1, 2), (2, 0)])
[]
>>> topo_kahn(3, [])
[0, 1, 2]                     # any order of the three
```

## Constraints

- `1 <= n <= 10**5`, `0 <= len(edges) <= 2 * 10**5`. `O(n + E)` time.

## Think about

Why does a vertex that sits on a cycle never reach in-degree 0? And why do the vertices **behind** the cycle (reachable from it) never get there either?
