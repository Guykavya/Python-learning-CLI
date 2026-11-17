def to_matrix(n, edges, directed=False):
    m = [[0] * n for _ in range(n)]
    for u, v in edges:
        m[u][v] = 1
        if not directed:
            m[v][u] = 1
    return m


def to_edges(matrix, directed=False):
    n = len(matrix)
    out = []
    for u in range(n):
        start = 0 if directed else u
        for v in range(start, n):
            if matrix[u][v]:
                out.append((u, v))
    return out
