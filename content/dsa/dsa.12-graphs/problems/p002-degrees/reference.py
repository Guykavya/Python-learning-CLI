def degrees(n, edges, directed=False):
    if directed:
        indeg, outdeg = [0] * n, [0] * n
        for u, v in edges:
            outdeg[u] += 1
            indeg[v] += 1
        return indeg, outdeg
    deg = [0] * n
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    return deg
