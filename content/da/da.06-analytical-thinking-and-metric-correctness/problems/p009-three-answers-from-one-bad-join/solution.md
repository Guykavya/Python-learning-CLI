## Approach

Each number gets the table grain it belongs to. `jobs` is the distinct job count. `job_value` is a job-level column, so keep
one row per job before summing. `items` counts the non-missing `line_no`: `count()` skips the empty row of a job without lines.

## Code

```python
def correct_totals(joined):
    per_job = joined.drop_duplicates(subset=["job_id"])
    return {
        "jobs": int(joined["job_id"].nunique()),
        "job_value": int(per_job["quote_total"].sum()),
        "items": int(joined["line_no"].count()),
    }
```

## Complexity

O(n) for the three passes over n rows.

## Another way

`joined.groupby("job_id")["quote_total"].first().sum()` takes one value per job as well. The better fix is upstream: do not
join at all for a job-level number (`jobs["quote_total"].sum()`), and aggregate `items` first when you need both.
