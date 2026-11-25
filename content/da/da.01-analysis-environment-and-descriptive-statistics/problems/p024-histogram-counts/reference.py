def histogram_counts(values, bins, low=None, high=None):
    if bins < 1:
        raise ValueError("bins must be at least 1")
    if low is None or high is None:
        if not values:
            raise ValueError("empty list needs an explicit range")
        low = min(values) if low is None else low
        high = max(values) if high is None else high
    width = (high - low) / bins
    counts = [0] * bins
    outside = 0
    for x in values:
        if x < low or x > high:
            outside += 1
            continue
        i = 0 if width == 0 else min(int((x - low) / width), bins - 1)
        counts[i] += 1
    rows = []
    for i in range(bins):
        left = low + i * width
        right = high if i == bins - 1 else low + (i + 1) * width
        rows.append((left, right, counts[i]))
    return rows, outside
