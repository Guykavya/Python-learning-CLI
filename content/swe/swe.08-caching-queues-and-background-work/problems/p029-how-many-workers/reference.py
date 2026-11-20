import math


def workers_needed(arrival_per_s, seconds_per_job, target_utilisation=0.7):
    if not 0 < target_utilisation <= 1:
        raise ValueError(f"target_utilisation must be in (0, 1], got {target_utilisation}")
    if arrival_per_s < 0 or seconds_per_job < 0:
        raise ValueError("rates and times cannot be negative")
    busy = arrival_per_s * seconds_per_job                  # Little's law: workers busy on average
    return max(1, math.ceil(round(busy / target_utilisation, 9)))


def drain_seconds(backlog, arrival_per_s, capacity_per_s):
    if backlog <= 0:
        return 0.0
    if capacity_per_s <= arrival_per_s:
        return float("inf")
    return backlog / (capacity_per_s - arrival_per_s)


def admit(queue_length, limit, retry_after=30):
    if queue_length >= limit:
        return 503, {"Retry-After": str(retry_after)}
    return 202, {}
