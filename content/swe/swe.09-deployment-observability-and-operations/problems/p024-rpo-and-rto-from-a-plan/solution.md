## Approach

```python
def worst_case_loss(backup_times, failure_time):
    before = [t for t in backup_times if t <= failure_time]
    if not before:
        raise ValueError("there is no backup at or before the failure")
    return (failure_time - max(before)).total_seconds() / 60


def worst_gap(backup_times):
    ordered = sorted(backup_times)
    if len(ordered) < 2:
        raise ValueError("need at least two backups to measure a gap")
    return max((b - a).total_seconds() for a, b in zip(ordered, ordered[1:])) / 60


def restore_time(size_gb, mb_per_s, fixed_minutes):
    if mb_per_s <= 0 or size_gb < 0 or fixed_minutes < 0:
        raise ValueError("need mb_per_s > 0 and non-negative size and fixed time")
    return fixed_minutes + size_gb * 1024 / mb_per_s / 60


def meets_targets(loss_minutes, restore_minutes, rpo_minutes, rto_minutes):
    return {"rpo_ok": loss_minutes <= rpo_minutes, "rto_ok": restore_minutes <= rto_minutes}
```

The chapter's answer to "Try it: RPO and RTO": nightly backups give an RPO of up to 24 hours (here 13.5 hours were lost) and an RTO of about 45 minutes plus the time to notice and decide. The cheapest improvement is more frequent backups (a smaller RPO) and a rehearsed runbook (a smaller RTO); whether it is worth it depends on what an hour of lost orders costs, and **that number decides**, not the technology.

## Complexity

O(n) for `worst_case_loss`, O(n log n) for `worst_gap` (sorting).

## Another way

Measure instead of estimate: a restore drill (problem p028) reports how long the restore really took (your measured RTO) and how old the data was (your measured RPO). A plan on paper says what you hope; a drill says what you have.
