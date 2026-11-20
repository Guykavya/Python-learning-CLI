def hit_ratio(events):
    # TODO: hits / (hits + misses); 0.0 for an empty list; ValueError for anything else
    return -1.0


def mean_latency(ratio, lookup_ms, db_ms):
    # TODO: every request pays the lookup; misses also pay the database
    return -1.0


def break_even_ratio(lookup_ms, db_ms):
    # TODO: solve lookup + (1 - r) * db == db for r; None if the cache can never help
    return -1.0
