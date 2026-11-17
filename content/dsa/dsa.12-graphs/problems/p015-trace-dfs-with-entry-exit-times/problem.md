# Trace DFS with entry/exit times

Many graph algorithms (topological sort, cycle detection, strongly connected components, bridges) need to know **when** DFS enters a vertex and when it **leaves** it, after all of its descendants are done (chapter section 4, "A DFS that knows when it leaves a vertex"). One clock counts both kinds of events.

Predict **exactly** what this program prints. Do not run it.

```python
def dfs_times(adj, start):
    tin, tout = {}, {}
    clock = 0

    def visit(u):
        nonlocal clock
        tin[u] = clock
        clock += 1
        print(f"enter {u} at {tin[u]}")
        for v in adj[u]:
            if v not in tin:
                visit(v)
        tout[u] = clock
        clock += 1
        print(f"exit {u} at {tout[u]}")

    visit(start)
    return tin, tout


n = 6
edges = [(0, 1), (0, 4), (1, 2), (3, 1), (2, 3), (4, 5)]
adj = [[] for _ in range(n)]
for u, v in edges:
    adj[u].append(v)
    adj[v].append(u)

tin, tout = dfs_times(adj, 0)
for u in range(n):
    print(u, tin[u], tout[u])
```

Write your answer in `answer.txt`, one printed line per line: first the 12 `enter`/`exit` lines, then six lines `u tin tout` for `u = 0 .. 5`.

## How to work

1. Write the adjacency lists in edge-list order. Careful with `(3, 1)`: it appends `1` to `adj[3]` **and** `3` to `adj[1]`, at the moment that edge is read.
2. Keep a stack of the calls that are still running (the vertex at the bottom is `0`). An `enter` line pushes, an `exit` line pops.
3. The clock goes up by one after **every** line of the first part.

## After you answer

1. When `1` is exited, its neighbour `3` was not visited **from** `1`. Why not?
2. A vertex `v` is in the DFS subtree of `u` exactly when `tin[u] < tin[v]` and `tout[v] < tout[u]`. Which vertices are in the subtree of `1`? Check with the numbers.
3. The enter/exit lines nest like brackets. Write them as a bracket string, for example `(0 (1 ... 1) ... 0)`.
