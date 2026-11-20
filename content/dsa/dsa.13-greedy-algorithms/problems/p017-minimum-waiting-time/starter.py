def min_total_waiting(durations):
    """Smallest possible sum of waiting times on one machine."""
    wait = 0
    elapsed = 0
    for d in durations:
        wait += elapsed
        elapsed += d
    return wait
