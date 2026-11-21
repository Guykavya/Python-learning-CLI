# Why are the servers uneven?

Chapter section 14.3 (load balancing: how requests are spread) and "Try it: why did the servers get uneven?". A load balancer picks a server for each request. **Round robin** (`1, 2, 3, 1, 2, 3...`) is fine when requests cost about the same; when some requests are far heavier it keeps stacking new requests behind a server that is stuck on a slow one. **Least connections** looks at what is *currently running* and sends the request to the server with the fewest requests in flight. Simulate both and see.

## The model

- Requests arrive **one per time unit**: request `i` arrives at time `i` (`0, 1, 2, ...`) and needs `durations[i]` time units of work.
- Each server handles **one request at a time**, **first come, first served**: a request starts at `max(arrival, time the server becomes free)` and ends `duration` later. The time between arrival and start is its **wait**.
- A request is **in flight** on its server at time `t` if it was assigned there and has **not finished yet**: its end time is **greater than** `t`.

## What to write

```python
def simulate(policy, durations, servers) -> dict: ...
```

- `policy` is `"round_robin"` (request `i` goes to server `i % servers`) or `"least_connections"` (the server with the fewest requests in flight **at the arrival time**; ties go to the lowest-numbered server). Any other policy raises `ValueError`; `servers < 1` raises `ValueError`.
- Return `{"requests": [...], "busy": [...], "max_wait": ...}`: per server the **number of requests** it received and the **total work time** it did (the sum of the durations assigned to it), and the **largest wait** of any request.

## Example

8 requests on 2 servers, the first one heavy: `durations = [6, 1, 1, 1, 1, 1, 1, 1]`.

```python
simulate("round_robin", durations, 2)
# {'requests': [4, 4], 'busy': [9, 4], 'max_wait': 4}      server 0 got the heavy request AND every other request after it
simulate("least_connections", durations, 2)
# {'requests': [1, 7], 'busy': [6, 7], 'max_wait': 0}      server 0 keeps the heavy request, server 1 takes everything else
```

Round robin gave server 0 a queue (the request that arrives at time 2 waits until time 6); least connections saw that server 0 was busy and used server 1.
