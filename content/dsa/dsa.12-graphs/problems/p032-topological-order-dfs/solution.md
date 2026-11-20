## Approach

Look at any edge `u -> v` when the DFS handles it. If `v` is WHITE, it is explored inside `u`'s visit and finishes **before** `u`. If `v` is BLACK, it finished earlier. If `v` is GREY, it is on the current path: `v` reaches `u` and `u` reaches `v`, which is a cycle. So in a DAG every edge `u -> v` has `v` finishing before `u`, and reversing the finishing order puts `u` before `v` (chapter section 7).

The DFS keeps `(vertex, iterator)` pairs on a stack instead of recursing: each loop step asks the vertex on top for its next neighbour; an exhausted iterator means the vertex is finished.

```python
WHITE, GREY, BLACK = 0, 1, 2


def topo_dfs(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    colour = [WHITE] * n
    finished = []
    for s in range(n):
        if colour[s] != WHITE:
            continue
        colour[s] = GREY
        stack = [(s, iter(adj[s]))]
        while stack:
            u, it = stack[-1]
            v = next(it, None)
            if v is None:
                colour[u] = BLACK
                finished.append(u)                 # everything after u is done
                stack.pop()
            elif colour[v] == GREY:
                return []                          # back edge: a cycle
            elif colour[v] == WHITE:
                colour[v] = GREY
                stack.append((v, iter(adj[v])))
    return finished[::-1]
```

For the diamond `0 -> 1, 0 -> 2, 1 -> 3, 2 -> 3` the DFS from 0 goes to 1, then 3; 3 finishes, then 1; then 2 (3 is BLACK, skipped) finishes, then 0. `finished = [3, 1, 2, 0]`, reversed `[0, 2, 1, 3]`.

## Complexity

Each vertex is pushed once and each edge followed once: `O(n + E)`.

## Another way

Kahn's algorithm (p031), which needs no DFS and no colours. A recursive DFS is the shortest code, but only for small graphs: on a chain of 100,000 vertices it passes the recursion limit (chapter section 4).
