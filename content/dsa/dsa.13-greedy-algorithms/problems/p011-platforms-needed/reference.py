def min_platforms(arrivals, departures):
    """Fewest platforms so no train waits; a departure at t frees a platform for an arrival at t."""
    arr = sorted(arrivals)
    dep = sorted(departures)
    i = j = 0
    on_platform = best = 0
    while i < len(arr):
        if arr[i] < dep[j]:        # the next event is an arrival
            on_platform += 1
            best = max(best, on_platform)
            i += 1
        else:                      # a departure (also when the times are equal)
            on_platform -= 1
            j += 1
    return best
