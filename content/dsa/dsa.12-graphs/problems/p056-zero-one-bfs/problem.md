# 0-1 BFS

Write `zero_one_bfs(n, edges, source)`. The graph has vertices `0 .. n-1` and **directed** edges `(u, v, w)` whose weight `w` is only ever `0` or `1`. Return the list of shortest distances from `source`, with `float("inf")` for vertices that cannot be reached.

Use the trick of chapter section 11: a **deque** instead of a heap. An edge of weight 0 leads to a vertex at the **same** distance, so it goes to the **front** (`appendleft`); an edge of weight 1 goes to the **back** (`append`). Compare distances (`dist[u] + w < dist[v]`), not a "seen" flag, because a vertex reached first through a 1-edge can later be reached for free.

Rules:

- Do not import `heapq` (the tests check your source): this exercise is about the deque.
- Parallel edges and self loops can appear. Do not change `edges`.

## Example

```python
>>> zero_one_bfs(4, [(0, 1, 1), (0, 2, 0), (2, 1, 0), (1, 3, 1)], 0)
[0, 0, 0, 1]
```

Vertex 1 is reached first through the edge `0 -> 1` of weight 1, but `0 -> 2 -> 1` costs `0 + 0 = 0`.

## Constraints

- `1 <= n <= 10**5`, `0 <= len(edges) <= 3 * 10**5`. `O(V + E)` time.

## Think about

Why is the deque always "sorted" (distances `d ... d` followed by `d + 1 ... d + 1`)? What goes wrong if the 0-edges are appended at the back as well, while you mark vertices as seen when you first reach them?
