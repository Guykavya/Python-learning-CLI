## Hint 1

All four definitions share the same test: `start <= t < end`. Which column does each one apply it to? Which two also
need the status? For the IST version, what do you add to `completed_at`, and does it change the column in `jobs`?

## Hint 2

```text
in_feb(series) = (series >= Feb 1) & (series < Mar 1)
by_created        -> in_feb(created_at)
by_started        -> in_feb(started_at)
by_completed      -> status == "completed" and in_feb(completed_at)
by_completed_ist  -> status == "completed" and in_feb(completed_at + 5h30)
anything else     -> raise ValueError with the name in the message
count the True values and return an int
```
