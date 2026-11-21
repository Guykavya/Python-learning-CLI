def simulate(policy, durations, servers):
    if servers < 1:
        raise ValueError("need at least one server")
    if policy not in ("round_robin", "least_connections"):
        raise ValueError(f"unknown policy {policy!r}")
    free_at = [0] * servers                          # when each server finishes its queue
    ends = [[] for _ in range(servers)]              # end times of the requests assigned to each server
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
