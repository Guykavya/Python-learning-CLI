import heapq


def network_delay_time(times, n, k):
    adj = [[] for _ in range(n + 1)]
    for u, v, t in times:
        adj[u].append((v, t))
    INF = float("inf")
    dist = [INF] * (n + 1)
    dist[k] = 0
    heap = [(0, k)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, t in adj[u]:
            if d + t < dist[v]:
                dist[v] = d + t
                heapq.heappush(heap, (d + t, v))
    worst = max(dist[1:])
    return -1 if worst == INF else worst
