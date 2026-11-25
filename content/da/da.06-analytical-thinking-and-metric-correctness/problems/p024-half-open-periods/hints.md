## Hint 1

Which of the two ends of the period is allowed to equal the timestamp, and which is not? What does a comparison such
as `NaT >= start` give in pandas: `True`, `False` or an error? What do you get when you combine two boolean Series?

## Hint 2

```text
start_ts = pd.Timestamp(start); end_ts = pd.Timestamp(end)
return (s >= start_ts) & (s < end_ts)      # start included, end excluded
# NaT compared with anything is False, so NaT falls out by itself
```
