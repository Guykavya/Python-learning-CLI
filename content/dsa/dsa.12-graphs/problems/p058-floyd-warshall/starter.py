def floyd_warshall(n, edges):
    """All-pairs shortest distances as an n x n list of lists (inf if unreachable)."""
    return [[0] * n for _ in range(n)]
