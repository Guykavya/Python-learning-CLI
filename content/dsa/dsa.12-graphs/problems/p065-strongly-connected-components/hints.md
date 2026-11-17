## Hint 1

Kosaraju in three steps: (1) run DFS over the whole graph and record each vertex when it **finishes**; (2) build the reversed graph (every edge `u -> v` becomes `v -> u`); (3) take the vertices from the **last** to finish to the first; each one that has no component yet starts a search in the reversed graph, and everything that search reaches (and is still unassigned) is one component.

## Hint 2

The finish order needs a DFS that knows when it **leaves** a vertex. Without recursion: keep a stack of `(vertex, iterator over its neighbours)`. Look at the top: take the next neighbour; if it is new, push it; if the iterator is empty, the vertex finishes: record it and pop. The second pass only needs reachability, so any stack or queue works there.

## Hint 3

```
order = []                                # finish order
for s in range(n): if not seen[s]: iterative DFS from s with (u, iter(adj[u])) frames, append u when its iterator is empty
radj = reversed edges
comp = [-1] * n;  result = []
for s in reversed(order):
    if comp[s] == -1:
        group = [s];  comp[s] = len(result);  stack = [s]
        while stack: u = stack.pop(); for v in radj[u]: if comp[v] == -1: comp[v] = len(result); group.append(v); stack.append(v)
        result.append(group)
return result
```
