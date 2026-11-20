def hit_ratio(events):
    hits = misses = 0
    for event in events:
        if event == "hit":
            hits += 1
        elif event == "miss":
            misses += 1
        else:
            raise ValueError(f"unknown event {event!r}: expected 'hit' or 'miss'")
    total = hits + misses
    return hits / total if total else 0.0


def mean_latency(ratio, lookup_ms, db_ms):
    if not 0.0 <= ratio <= 1.0:
        raise ValueError(f"ratio must be between 0 and 1, got {ratio}")
    return lookup_ms + (1.0 - ratio) * db_ms


def break_even_ratio(lookup_ms, db_ms):
    if lookup_ms >= db_ms:
        return None
    return lookup_ms / db_ms
