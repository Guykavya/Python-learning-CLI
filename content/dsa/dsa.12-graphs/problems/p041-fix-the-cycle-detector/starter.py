def has_cycle(graph):
    """True if the import graph has a directed cycle."""
    visited = set()

    def visit(u):
        visited.add(u)
        for v in graph[u]:
            if v in visited or visit(v):
                return True
        return False

    return any(u not in visited and visit(u) for u in graph)
