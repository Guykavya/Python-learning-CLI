import math


def has_arbitrage(n, rates):
    EPS = 1e-12
    edges = [(a, b, -math.log(r)) for a, b, r in rates]
    dist = [0.0] * n
    for _ in range(n):
        changed = False
        for a, b, w in edges:
            if dist[a] + w < dist[b] - EPS:
                dist[b] = dist[a] + w
                changed = True
        if not changed:
            return False
    return True
