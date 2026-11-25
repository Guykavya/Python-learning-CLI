## Hint 1

Write the windows by hand for a few dates: which recorded days lie between `date - 6 days` and `date`? `rolling` accepts
a time span such as `"7D"` instead of a row count. What does it need the dates to be (where, and in what order)?

## Hint 2

```text
d = daily.sort_values("date")
s = d.set_index("date")["revenue"]         (a time window needs a sorted DatetimeIndex)
week = s.rolling("7D").sum()               (the window (date - 7 days, date] = date-6 .. date)
return d with week_total = week values, fresh index
```
