def random_tree(n, rng, shape="random"):
    if shape not in ("random", "path", "star"):
        raise ValueError(f"unknown shape: {shape}")
    if n == 1:
        return []
    parent = [0] * n
    for i in range(1, n):
        if shape == "random":
            parent[i] = rng.randrange(i)
        elif shape == "path":
            parent[i] = i - 1
        else:
            parent[i] = 0
    perm = list(range(1, n + 1))
    rng.shuffle(perm)
    edges = []
    for i in range(1, n):
        u, v = perm[parent[i]], perm[i]
        if rng.random() < 0.5:
            u, v = v, u
        edges.append((u, v))
    rng.shuffle(edges)
    return edges
