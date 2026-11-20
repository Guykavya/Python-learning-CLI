import random

from solution import network_delay_time

INF = float("inf")


def slow(times, n, k):
    """Bellman-Ford over servers 1..n: simple and obviously right."""
    dist = [INF] * (n + 1)
    dist[k] = 0
    for _ in range(n):
        for u, v, t in times:
            if dist[u] + t < dist[v]:
                dist[v] = dist[u] + t
    worst = max(dist[1:])
    return -1 if worst == INF else worst


def test_the_examples():
    assert network_delay_time([(2, 1, 1), (2, 3, 1), (3, 4, 1)], 4, 2) == 2, (
        "from server 2: servers 1 and 3 after 1 ms, server 4 after 2 ms, so all have it at 2.")
    assert network_delay_time([(1, 2, 1)], 2, 1) == 1, "one link 1 -> 2 of 1 ms: answer 1."
    assert network_delay_time([(1, 2, 1)], 2, 2) == -1, "from server 2 the link 1 -> 2 is useless (one-way): server 1 never gets it, -1."


def test_the_answer_is_the_largest_distance_not_the_sum():
    got = network_delay_time([(1, 2, 3), (1, 3, 4)], 3, 1)
    assert got == 4, f"the signal goes to 2 and 3 at the same time: the answer is max(3, 4) = 4, not 3 + 4. Got {got}."


def test_shortest_route_not_first_route():
    got = network_delay_time([(1, 2, 10), (1, 3, 1), (3, 2, 1)], 3, 1)
    assert got == 2, f"server 2 is reached through 3 after 1 + 1 = 2 ms, earlier than the direct 10 ms link. Got {got}."


def test_servers_are_numbered_from_one():
    got = network_delay_time([(1, 2, 5), (2, 3, 5)], 3, 1)
    assert got == 10, f"servers are 1..n: server 3 gets the signal at 10. Got {got}. (A list of size n has no index n.)"


def test_a_server_with_no_links_is_never_reached():
    got = network_delay_time([(1, 2, 1)], 3, 1)
    assert got == -1, f"server 3 has no link at all, so it never receives the signal: -1. Got {got}."


def test_single_server():
    assert network_delay_time([], 1, 1) == 0, "one server: it already has the signal at time 0."


def test_links_are_one_way():
    assert network_delay_time([(2, 1, 1)], 2, 1) == -1, "the link goes 2 -> 1; from 1 the signal cannot reach 2: -1."


def test_zero_delays_and_parallel_links():
    assert network_delay_time([(1, 2, 0), (2, 3, 0)], 3, 1) == 0, "0 ms links: everything has the signal at time 0."
    assert network_delay_time([(1, 2, 9), (1, 2, 4)], 2, 1) == 4, "two links 1 -> 2: the faster one (4 ms) counts."


def test_random_networks():
    rng = random.Random(51)
    for _ in range(300):
        n = rng.randint(1, 9)
        times = [(rng.randint(1, n), rng.randint(1, n), rng.randint(0, 20)) for _ in range(rng.randint(0, 25))]
        k = rng.randint(1, n)
        want = slow(times, n, k)
        got = network_delay_time(times, n, k)
        assert got == want, f"network_delay_time({times}, {n}, {k}): expected {want}, got {got}."


def test_bigger_network():
    rng = random.Random(510)
    n = 10000
    times = [(i, i + 1, rng.randint(0, 100)) for i in range(1, n)]
    times += [(rng.randint(1, n), rng.randint(1, n), rng.randint(0, 100)) for _ in range(50000)]
    rng.shuffle(times)
    got = network_delay_time(times, n, 1)
    assert got == slow_dijkstra(times, n, 1), "wrong answer on a network with 10,000 servers and 60,000 links."


def slow_dijkstra(times, n, k):
    import heapq
    adj = [[] for _ in range(n + 1)]
    for u, v, t in times:
        adj[u].append((v, t))
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
    w = max(dist[1:])
    return -1 if w == INF else w
