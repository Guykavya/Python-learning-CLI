WHITE, GREY, BLACK = 0, 1, 2


def has_cycle_directed(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    colour = [WHITE] * n
    for s in range(n):
        if colour[s] != WHITE:
            continue
        colour[s] = GREY
        stack = [(s, iter(adj[s]))]
        while stack:
            u, it = stack[-1]
            v = next(it, None)
            if v is None:
                colour[u] = BLACK                  # finished: no cycle through u
                stack.pop()
            elif colour[v] == GREY:
                return True                        # back edge to the current path
            elif colour[v] == WHITE:
                colour[v] = GREY
                stack.append((v, iter(adj[v])))
    return False
