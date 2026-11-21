## Hint 1

Picture the buckets as shelves. If 100 requests are sorted from fastest to slowest, the 95th request is "at rank 95". Which shelf holds it? The counts are cumulative, so the shelf is the first one whose count reaches the rank. Inside that shelf you do not know the exact times, so assume the requests are spread evenly between the shelf's two bounds.

## Hint 2

```text
total = last count; if total == 0: nan
rank = q * total
for i, (le, count) in enumerate(buckets):
    if count >= rank:
        if le is inf: return the last finite le
        lower, before = previous (le, count), or (0.0, 0) for the first bucket
        return lower + (le - lower) * (rank - before) / (count - before)
```

Validate first (q range, le strictly increasing, counts not decreasing, last le infinite), so the division can never be by zero: when `count >= rank` is the first time, `count > before`... except for an empty first shelf and `rank` of 0, which `0 < q` rules out.
