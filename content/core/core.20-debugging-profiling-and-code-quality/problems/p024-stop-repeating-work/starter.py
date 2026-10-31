def top_k_each_day(events, k):
    """events: list of (day, score). Return {day: the k highest scores of that day, highest first}."""
    result = {}
    for day, score in events:
        scores = sorted([s for d, s in events if d == day], reverse=True)
        result[day] = scores[:k]
    return result
