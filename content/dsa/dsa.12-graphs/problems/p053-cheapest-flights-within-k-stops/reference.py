def find_cheapest_price(n, flights, src, dst, k):
    INF = float("inf")
    dist = [INF] * n
    dist[src] = 0
    for _ in range(k + 1):
        prev = dist[:]
        for u, v, price in flights:
            if prev[u] + price < dist[v]:
                dist[v] = prev[u] + price
    return -1 if dist[dst] == INF else dist[dst]
