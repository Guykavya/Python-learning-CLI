WHITE, GREY, BLACK = 0, 1, 2


def topo_dfs(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    colour = [WHITE] * n
    finished = []
    for s in range(n):
        if colour[s] != WHITE:
            continue
        colour[s] = GREY
        stack = [(s, iter(adj[s]))]
        while stack:
            u, it = stack[-1]
            v = next(it, None)
            if v is None:
                colour[u] = BLACK
                finished.append(u)                 # everything after u is done
                stack.pop()
            elif colour[v] == GREY:
                return []                          # back edge: a cycle
            elif colour[v] == WHITE:
                colour[v] = GREY
                stack.append((v, iter(adj[v])))
    return finished[::-1]
