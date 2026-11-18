def min_total_waiting(durations):
    """Smallest possible sum of waiting times on one machine."""
    wait = 0
    elapsed = 0
    for d in sorted(durations):        # shortest job first
        wait += elapsed                # this job waited for everything before it
        elapsed += d
    return wait
