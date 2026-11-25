# Periods and month ends

Chapter sections 13.3, 13.4 and 13.6. Months are not all the same length, so "one month later" and "the end of the
month" are not the same as "30 days later". pandas has three tools for this: a **Period** (a whole month as one
value), `DateOffset(months=n)` (move by calendar months, clipping to the last day if needed) and `MonthEnd(n)` (roll
forward to a month end).

```python
import pandas as pd

days = pd.Series(pd.to_datetime(["2024-01-31", "2024-02-10", "2023-12-15"]))
print(days.dt.to_period("M").astype(str).tolist())

jan31 = pd.Timestamp("2024-01-31")
jan15 = pd.Timestamp("2024-01-15")
print((jan31 + pd.DateOffset(months=1)).strftime("%Y-%m-%d"))
print((jan31 + pd.offsets.MonthEnd(1)).strftime("%Y-%m-%d"))
print((jan31 + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d"))
print((jan15 + pd.offsets.MonthEnd(1)).strftime("%Y-%m-%d"), (jan15 + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d"))
print((pd.Timestamp("2024-03-31") + pd.DateOffset(months=-1)).strftime("%Y-%m-%d"))

feb = pd.Series(pd.to_datetime(["2024-02-10", "2023-02-10", "2100-02-10"]))
print(feb.dt.days_in_month.tolist())
print(str(pd.Period("2024-01", "M") + 1))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Datetimes are printed as
`YYYY-MM-DD` text, so you do not have to guess how a Timestamp looks. Remember that 2024 is a leap year and 2100 is not.

Do not run the code before you have written your answer.

## Example

For `pd.Timestamp("2024-04-10") + pd.offsets.MonthEnd(1)` the program would print `2024-04-30`: the next month end on
or after the 10th of April.

## After you answer

- `MonthEnd(1)` and `MonthEnd(0)` gave different answers for one of the two dates. Which one, and why?
- Why does `DateOffset(months=1)` on 31 January not give "31 February"?
