# RPO and RTO from a plan

Chapter sections 13.1 (the only backup that counts is one you have restored) and 13.4 (make it routine), and "Try it: RPO and RTO". Two numbers define what a backup plan really gives you:

- **RPO** (recovery point objective): how much recent data you can lose. With nightly backups the **worst case** is the time since the last good backup at the moment of the failure.
- **RTO** (recovery time objective): how long recovery takes: the time to copy the data back plus the fixed work (finding the backup, starting the service, checking it).

Write four small functions that compute them from a plan and compare with the targets a business set.

## What to write

```python
def worst_case_loss(backup_times: list[datetime], failure_time: datetime) -> float: ...
def worst_gap(backup_times: list[datetime]) -> float: ...
def restore_time(size_gb: float, mb_per_s: float, fixed_minutes: float) -> float: ...
def meets_targets(loss_minutes, restore_minutes, rpo_minutes, rto_minutes) -> dict: ...
```

All results are in **minutes** (floats).

- `worst_case_loss(backup_times, failure_time)`: the minutes between the **latest backup that is not after** `failure_time` and `failure_time`. A backup taken exactly at the failure time loses 0. If there is no backup at or before the failure, raise `ValueError`. `backup_times` may be in any order.
- `worst_gap(backup_times)`: the longest gap between two **consecutive** backups (sorted by time) in minutes: the real RPO of the schedule, because a failure just before the next backup loses the whole gap. Fewer than 2 backups: raise `ValueError`.
- `restore_time(size_gb, mb_per_s, fixed_minutes)`: `fixed_minutes + size_gb * 1024 / mb_per_s / 60`. Raise `ValueError` if `mb_per_s <= 0` or a number is negative.
- `meets_targets(...)` returns `{"rpo_ok": loss_minutes <= rpo_minutes, "rto_ok": restore_minutes <= rto_minutes}`.

## Example

The chapter's case: a backup every night at 02:00; at 15:30 an operator drops the wrong table; restoring takes 45 minutes.

```python
nights = [datetime(2026, 11, d, 2, 0) for d in range(1, 10)]
worst_case_loss(nights, datetime(2026, 11, 9, 15, 30))   # 810.0   (13.5 hours of orders)
worst_gap(nights)                                         # 1440.0  (24 hours)
restore_time(size_gb=2, mb_per_s=100, fixed_minutes=30)   # 30 + 2 * 1024 / 100 / 60 = 30.34...
meets_targets(810, 45, rpo_minutes=60, rto_minutes=60)    # {'rpo_ok': False, 'rto_ok': True}
```
