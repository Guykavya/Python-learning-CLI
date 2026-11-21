import math


def _check(buckets):
    if not buckets or buckets[-1][0] != math.inf:
        raise ValueError("the last bucket must have le = infinity")
    for (prev_le, prev_count), (le, count) in zip(buckets, buckets[1:]):
        if le <= prev_le:
            raise ValueError("the le values must be strictly increasing")
        if count < prev_count:
            raise ValueError("cumulative counts cannot decrease")


def quantile(q, buckets):
    if not 0 < q <= 1:
        raise ValueError(f"q must be in (0, 1], got {q}")
    _check(buckets)
    total = buckets[-1][1]
    if total == 0:
        return math.nan
    rank = q * total
    for i, (le, count) in enumerate(buckets):
        if count >= rank:
            if le == math.inf:
                return buckets[-2][0] if len(buckets) > 1 else math.nan
            lower, before = (buckets[i - 1][0], buckets[i - 1][1]) if i > 0 else (0.0, 0)
            return lower + (le - lower) * (rank - before) / (count - before)
    return math.nan


def summary(buckets, total_seconds):
    total = buckets[-1][1]
    return {"mean": total_seconds / total if total else 0.0,
            "p50": quantile(0.5, buckets), "p95": quantile(0.95, buckets), "p99": quantile(0.99, buckets)}
