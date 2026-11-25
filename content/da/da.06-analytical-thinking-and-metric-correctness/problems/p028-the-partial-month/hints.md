## Hint 1

Which jobs exist at the cut? How do you turn a timestamp into a month label like `2025-03`? For a month label, what
is the first instant of the *next* month, and what must be true about it, compared with the cut, for the month to be
unfinished?

## Hint 2

```text
cut = pd.Timestamp(cut)
seen = jobs where created_at < cut
month = seen.created_at formatted "%Y-%m";  counts = number of rows per month (sorted)
out = table with columns month, jobs
next_start = first day of month + one month (pd.offsets.MonthBegin(1) after parsing month + "-01")
out["is_partial"] = next_start > cut
reset the index; make jobs int
```
