## Hint 1

Keep, for every server, the time at which it will have finished everything assigned to it so far (`free_at`) and the list of end times of its requests. For each arriving request: choose the server by the policy, then `start = max(arrival, free_at[server])`, `end = start + duration`. For least connections, count how many end times of each server are **greater than** the arrival time.

## Hint 2

```text
for i, duration in enumerate(durations):  arrival = i
    round_robin: s = i % servers
    least_connections: in_flight[k] = number of ends[k] > arrival; s = the k with the smallest (in_flight[k], k)
    start = max(arrival, free_at[s]); free_at[s] = start + duration; ends[s].append(free_at[s])
    requests[s] += 1; busy[s] += duration; max_wait = max(max_wait, start - arrival)
```
