## Hint 1

Is the shift done before or after you cut the timestamp to a date? What shift is "UTC to IST", in hours and minutes?
Which pandas method gives the number of rows per distinct value, and how do you get the dates in order?

## Hint 2

```text
local = jobs["created_at"] + pd.Timedelta(hours=5, minutes=30)     # a new Series; jobs is untouched
day   = local.dt.strftime("%Y-%m-%d")
counts = day.value_counts().sort_index()
return {date: int(n) for date, n in counts.items()}
```
