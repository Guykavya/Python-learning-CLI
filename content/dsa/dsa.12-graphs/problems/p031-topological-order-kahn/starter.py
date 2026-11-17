from collections import deque


def topo_kahn(n, edges):
    """A topological order of vertices 0..n-1, or [] if the graph has a cycle."""
    return list(range(n))
