def redundant_edge(n, edges):
    parent = list(range(n))
    size = [1] * n

    def find(x):
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            return (u, v)                          # u and v were already connected
        if size[ru] < size[rv]:
            ru, rv = rv, ru
        parent[rv] = ru
        size[ru] += size[rv]
    return None                                    # not reached for valid input
