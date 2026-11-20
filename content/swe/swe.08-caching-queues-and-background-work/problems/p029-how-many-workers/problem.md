# How many workers?

Chapter sections 15.3 (Little's law) and 15.4 (backpressure). **Little's law**: busy workers on average = jobs arriving per second x seconds per job. A pool that runs at 100% has no room for a burst, so you size it for a **target utilisation** below 1 (for example 70%).

## What to write

```python
def workers_needed(arrival_per_s, seconds_per_job, target_utilisation=0.7) -> int: ...
def drain_seconds(backlog, arrival_per_s, capacity_per_s) -> float: ...
def admit(queue_length, limit, retry_after=30) -> tuple[int, dict]: ...
```

- `workers_needed`: `busy = arrival_per_s * seconds_per_job`; return the smallest whole number of workers so that `busy / workers <= target_utilisation`, which is `ceil(busy / target_utilisation)`. Round `busy / target_utilisation` to 9 decimal places **before** `ceil`, because floats are not exact (`21 / 0.7` is `30.000000000000004`). At least 1 worker. Raise `ValueError` if `target_utilisation` is not in `(0, 1]` or a rate or time is negative.
- `drain_seconds`: how long a backlog takes to clear while new jobs keep arriving: `backlog / (capacity - arrival)`. If capacity is not above the arrival rate, it never drains: return `float("inf")`. An empty backlog takes `0.0`.
- `admit`: the backpressure decision for a new job. If `queue_length >= limit`, return `(503, {"Retry-After": "<retry_after>"})` (the header value is a string); otherwise `(202, {})`.

## Example

```python
workers_needed(20, 0.5)                 # busy 10 -> 10 / 0.7 = 14.29 -> 15
workers_needed(14, 1.5)                 # busy 21 -> exactly 30, not 31
drain_seconds(4440, 20, 26)             # 740.0 seconds (about 12 minutes)
drain_seconds(4440, 20, 20)             # inf
admit(3, 3)                             # (503, {'Retry-After': '30'})
admit(2, 3)                             # (202, {})
```
