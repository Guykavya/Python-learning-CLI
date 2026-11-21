## Approach

```python
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
```

This is the estimate behind `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` (chapter 10.5). It is only as good as the buckets: inside a bucket the requests are assumed to be evenly spread, so the answer is never more precise than the bucket width. Choose buckets around the latencies you care about (the SLO threshold, for example).

The lesson of `summary`: the mean of this histogram is 80 ms, the p99 is a full second. Users do not experience the average; the 1 in 100 who waited a second remember it, and the alert should fire on p95 or p99.

## Complexity

O(number of buckets) per quantile.

## Another way

Keep every latency and call `statistics.quantiles` or `numpy.percentile`: exact, but it needs memory proportional to the number of requests, which is why Prometheus uses histograms. Summaries (`quantile` labels computed in the client) are exact per instance but cannot be averaged across instances, which is why histograms are preferred.
