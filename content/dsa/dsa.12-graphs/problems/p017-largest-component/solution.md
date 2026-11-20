## Approach

Run the component loop from p016 with an iterative search that collects its vertices. Components are found in order of their smallest vertex (the outer loop goes `0, 1, 2, ...`, and a component is found at its smallest unseen vertex), so replacing the best only when the new one is **strictly** larger keeps the earlier one on ties.

## Code

```python
def largest_component(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * n
    best = []
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        comp, stack = [s], [s]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    comp.append(v)
                    stack.append(v)
        if len(comp) > len(best):
            best = comp
    return sorted(best)
```

## Complexity

`O(n + E)` for the searches and `O(k log k)` to sort the `k` vertices of the answer.

## Another way

Union-Find with sizes (section 9): after all unions, the root with the largest size is the answer; collect the vertices with that root. A `comp` label per vertex (chapter `components`) also works: count the labels, pick the biggest, filter.
