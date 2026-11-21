# Percentiles from a histogram

Chapter sections 10.4 (percentiles, not averages), 10.2 (the histogram) and 10.5 (the `SlowRequests` alert that uses `histogram_quantile(0.95, ...)`). The average hides the worst experiences: if 99 requests take 50 ms and one takes 5 seconds, the average is about 100 ms and looks fine. A histogram stores only **how many requests were at most `le` seconds** for a few values of `le` (cumulative buckets), so a percentile has to be **estimated**. This is what PromQL's `histogram_quantile` does; write it.

## What to write

```python
def quantile(q: float, buckets: list[tuple[float, int]]) -> float: ...
def summary(buckets: list[tuple[float, int]], total_seconds: float) -> dict: ...
```

`buckets` is a list of `(le, cumulative_count)` sorted by `le`, the last one being `(float("inf"), total)`. The counts are cumulative: `(0.25, 95)` means 95 requests took 0.25 s or less.

**`quantile(q, buckets)`** for `0 < q <= 1`:

1. `total` is the count of the last bucket. If `total == 0`, return `float("nan")`.
2. `rank = q * total`.
3. Find the **first** bucket whose cumulative count is `>= rank`.
4. If that bucket is the `+Inf` bucket, return the **upper bound of the highest finite bucket** (the histogram cannot say more).
5. Otherwise estimate by **linear interpolation** inside the bucket: with `lower` = the `le` of the previous bucket (`0.0` for the first bucket) and `before` = the cumulative count of the previous bucket (`0` for the first):

   `lower + (le - lower) * (rank - before) / (count - before)`

Raise `ValueError` if `q` is not in `(0, 1]`, if the `le` values are not strictly increasing, if the counts ever **decrease**, or if the last `le` is not infinite.

**`summary(buckets, total_seconds)`** returns `{"mean": total_seconds / total, "p50": ..., "p95": ..., "p99": ...}` (the mean is `0.0` if there are no requests; the percentiles are then `nan`).

## Example

```python
buckets = [(0.05, 80), (0.1, 90), (0.25, 95), (0.5, 97), (1.0, 99), (5.0, 100), (float("inf"), 100)]
quantile(0.5, buckets)    # rank 50, in the first bucket: 0 + 0.05 * 50 / 80 = 0.03125
quantile(0.95, buckets)   # rank 95: first bucket with count >= 95 is (0.25, 95): 0.1 + 0.15 * (95 - 90) / (95 - 90) = 0.25
quantile(0.99, buckets)   # rank 99: (1.0, 99): 0.5 + 0.5 * (99 - 97) / (99 - 97) = 1.0
summary(buckets, total_seconds=8.0)["mean"]    # 0.08: an 80 ms average hides a p99 of one second
```
