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
