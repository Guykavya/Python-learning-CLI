## Approach

```python
def estimate(dau, writes_per_user, reads_per_write, bytes_per_item, years, peak_factor):
    ...validation...
    avg_write = dau * writes_per_user / SECONDS_PER_DAY
    avg_read = avg_write * reads_per_write
    storage_gb = dau * writes_per_user * 365 * years * bytes_per_item / 1e9
    return {"avg_write_qps": round(avg_write, 2), "peak_write_qps": round(avg_write * peak_factor, 2),
            "avg_read_qps": round(avg_read, 2), "peak_read_qps": round(avg_read * peak_factor, 2),
            "storage_gb": round(storage_gb, 1)}
```

Read the results as decisions, as the chapter does (13.3): Taskboard peaks at about 25 reads per second and fits in under 100 GB, so **one database server and two app servers are plenty**; the social feed peaks at tens of thousands of reads per second and 65 TB, and now caching, replicas and partitioning are *required*. One ordinary database server on SSDs handles thousands of simple queries per second (chapter 13.4), so "50 requests per second" does not need a cluster. The most valuable question to add to every estimate is "**what about bursts?**" (the first minute of the school day).

## Complexity

O(1).

## Another way

Add an overhead factor of 2 to 4 for indexes and replicas when you size storage (the chapter's `estimate.py` uses 3). Here the formula is the raw data, which keeps the arithmetic checkable by hand.
