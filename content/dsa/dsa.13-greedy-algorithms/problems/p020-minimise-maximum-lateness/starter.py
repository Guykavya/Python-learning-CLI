def max_lateness(jobs, order):
    """jobs: list of (duration, deadline); order: list of indices. Return the largest lateness (0 if nobody is late)."""
    return -1


def best_order(jobs):
    """Return a list of indices whose maximum lateness is as small as possible."""
    return list(range(len(jobs)))
