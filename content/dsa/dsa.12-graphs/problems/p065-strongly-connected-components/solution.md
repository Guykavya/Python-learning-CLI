## Approach

The vertex that finishes last in a DFS of the whole graph lies in a **source** component of the condensation (nothing outside points into it). In the reversed graph that component is a **sink**: a search from that vertex cannot leave it, so it collects exactly that component. Removing it, the next unassigned vertex in decreasing finish order is again in a source of what remains, and so on. Both passes are written with explicit stacks, so a chain of `10**5` vertices is fine.

## Code

```python
def strongly_connected_components(n, edges):
    adj = [[] for _ in range(n)]
    radj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        radj[v].append(u)
    seen = [False] * n
    order = []
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        stack = [(s, iter(adj[s]))]
        while stack:
            u, it = stack[-1]
            v = next(it, None)
            if v is None:
                order.append(u)                  # u finishes
                stack.pop()
            elif not seen[v]:
                seen[v] = True
                stack.append((v, iter(adj[v])))
    comp = [-1] * n
    result = []
    for s in reversed(order):                    # latest finish first
        if comp[s] != -1:
            continue
        cid = len(result)
        comp[s] = cid
        group = [s]
        stack = [s]
        while stack:
            u = stack.pop()
            for v in radj[u]:
                if comp[v] == -1:
                    comp[v] = cid
                    group.append(v)
                    stack.append(v)
        result.append(group)
    return result
```

## Complexity

Two passes over all vertices and edges plus the reversed graph: `O(V + E)` time and memory.

## Another way

**Tarjan's algorithm** finds the components in one DFS with `index` and `low` values and a stack of "open" vertices; a vertex with `low == index` is the root of a component, which is popped off the stack. It needs no reversed graph, but written without recursion it is fiddlier (the `low` of a child must be passed to its parent when the child finishes). Kosaraju emits the components in topological order of the condensation, Tarjan in reverse.
