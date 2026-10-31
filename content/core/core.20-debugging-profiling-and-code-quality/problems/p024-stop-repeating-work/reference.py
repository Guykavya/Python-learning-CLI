def top_k_each_day(events, k):
    """events: list of (day, score). Return {day: the k highest scores of that day, highest first}."""
    by_day = {}
    for day, score in events:
        by_day.setdefault(day, []).append(score)
    return {day: sorted(scores, reverse=True)[:k] for day, scores in by_day.items()}
