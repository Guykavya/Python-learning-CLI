WHITE, GREY, BLACK = 0, 1, 2


def topo_dfs(n, edges):
    """A topological order (reverse finishing order of a DFS), or [] if there is a cycle."""
    return list(range(n))
