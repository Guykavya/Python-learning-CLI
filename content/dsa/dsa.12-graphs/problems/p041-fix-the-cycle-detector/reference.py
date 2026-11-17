WHITE, GREY, BLACK = 0, 1, 2


def has_cycle(graph):
    """True if the import graph has a directed cycle."""
    colour = {u: WHITE for u in graph}

    def visit(u):
        colour[u] = GREY                       # on the current path
        for v in graph[u]:
            if colour[v] == GREY:
                return True                    # back to the current path: a cycle
            if colour[v] == WHITE and visit(v):
                return True
        colour[u] = BLACK                      # finished: safe for ever
        return False

    return any(colour[u] == WHITE and visit(u) for u in graph)
