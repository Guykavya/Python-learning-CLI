INF = float("inf")


def shortest_tour(dist):
    n = len(dist)
    if n == 1:
        return 0, [0]
    full = (1 << n) - 1
    f = [[INF] * n for _ in range(1 << n)]       # f[mask][last]
    parent = [[None] * n for _ in range(1 << n)]
    f[1][0] = 0                                    # only place 0 visited, standing there
    for mask in range(1 << n):
        if not mask & 1:                           # every path starts at 0
            continue
        row = f[mask]
        for last in range(n):
            here = row[last]
            if here == INF:
                continue
            for nxt in range(n):
                if mask >> nxt & 1:                # already visited
                    continue
                new_mask = mask | (1 << nxt)
                cost = here + dist[last][nxt]
                if cost < f[new_mask][nxt]:
                    f[new_mask][nxt] = cost
                    parent[new_mask][nxt] = last
    length, last = min((f[full][last] + dist[last][0], last) for last in range(1, n))
    order, mask = [], full
    while last is not None:                        # walk back to place 0
        order.append(last)
        prev = parent[mask][last]
        mask &= ~(1 << last)
        last = prev
    order.reverse()
    return length, order
