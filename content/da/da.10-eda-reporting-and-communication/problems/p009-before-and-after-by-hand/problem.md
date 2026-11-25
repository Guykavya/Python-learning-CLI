# Before and after by hand

Chapter section 4.2. To compare "before" and "after" a change, you split a time series at a date. The question is always: **on which side does the split week itself go?**
Here, as in the chapter, the week that starts on the change date counts as **after**.

```python
import pandas as pd

weeks = pd.date_range("2024-08-05", periods=8, freq="W-MON")
churn = pd.Series([1.0, 1.2, 0.8, 1.0, 2.6, 2.4, 1.6, 2.0], index=weeks)
split = pd.Timestamp("2024-09-02")
before = churn[churn.index < split]
after = churn[churn.index >= split]
print(len(before), len(after))
print(f"{before.mean():.2f} {after.mean():.2f}")
print(f"{after.mean() - before.mean():+.2f}")
wrong = churn[churn.index > split]
print(len(wrong), f"{wrong.mean():.2f}")
```

`freq="W-MON"` gives weeks that start on Mondays: 5 August, 12 August, and so on. Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.
Do not run the code before you have written your answer.

## Example

With `split = pd.Timestamp("2024-08-12")`, the first line would be `1 7`.

## After you answer

- Which week does `wrong` lose, and how does that change the "after" mean?
- Why must a report state the rule for the boundary week?
