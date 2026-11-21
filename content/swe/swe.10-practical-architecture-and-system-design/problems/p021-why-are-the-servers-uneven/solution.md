## Approach

```python
def simulate(policy, durations, servers):
    free_at = [0] * servers
    ends = [[] for _ in range(servers)]
    requests, busy, max_wait = [0] * servers, [0] * servers, 0
    for i, duration in enumerate(durations):
        arrival = i
        if policy == "round_robin":
            s = i % servers
        else:
            in_flight = [sum(1 for end in ends[k] if end > arrival) for k in range(servers)]
            s = min(range(servers), key=lambda k: (in_flight[k], k))
        start = max(arrival, free_at[s])
        free_at[s] = start + duration
        ends[s].append(free_at[s])
        requests[s] += 1
        busy[s] += duration
        max_wait = max(max_wait, start - arrival)
    return {"requests": requests, "busy": busy, "max_wait": max_wait}
```

The chapter's simulation (14.3, 20,000 requests, 3% of them 400 ms) shows the same thing in the tail: round robin p99 = 1,331 ms, random 1,496 ms, least connections 733 ms. Round robin and random cannot see that a server is stuck on a heavy request, so they keep stacking new requests behind it; least connections sees the queue. Compare balancing by **percentiles**, never by the average alone. When all requests cost about the same, round robin is nearly as good and much simpler. (The answer to the chapter's "Try it: why did the servers get uneven?": skewed clients behind one IP with IP-hash, or `hash % N` with small N: use least connections for stateless apps and consistent hashing, p022, when affinity is needed.)

## Complexity

O(requests x servers x requests per server) with the simple in-flight count; fine for a simulation. A real balancer keeps a counter per server instead.

## Another way

Add a third policy, `random` with a seeded `random.Random`, and compare the three in the test: the result of random depends on the seed, which is why the chapter fixes its seeds to make the comparison repeatable.
