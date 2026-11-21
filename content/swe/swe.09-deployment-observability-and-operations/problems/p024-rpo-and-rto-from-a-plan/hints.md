## Hint 1

Subtracting two `datetime` objects gives a `timedelta`. Which method turns it into seconds, and how do you get minutes? For `worst_case_loss`, which of the backups matters: the first, the last, or the latest one that is not in the future?

## Hint 2

```text
worst_case_loss: before = [t for t in backups if t <= failure]; none -> ValueError; (failure - max(before)) in minutes
worst_gap: sort; maximum of (b - a) over neighbouring pairs, in minutes; fewer than 2 -> ValueError
restore_time: fixed_minutes + size_gb * 1024 / mb_per_s / 60
meets_targets: {"rpo_ok": loss <= rpo, "rto_ok": restore <= rto}
```
