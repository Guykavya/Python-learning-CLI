def schedule(jobs):
    """jobs: list of (name, duration). Return (names in run order, total waiting time)."""
    ordered = sorted(jobs, key=lambda job: job[1])
    order = []
    total_wait = 0
    elapsed = 0
    for name, duration in ordered:
        order.append(name)
        elapsed += duration
        total_wait = elapsed
    return order, total_wait
