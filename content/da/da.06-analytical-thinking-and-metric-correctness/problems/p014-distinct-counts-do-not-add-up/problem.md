# Distinct counts do not add up

Chapter section 5.2. Jobs are counted per customer for each month of a quarter. Add the monthly distinct counts and compare with the distinct customers of the whole quarter. The last row sits exactly on the end of the quarter.

```python
import pandas as pd

jobs = pd.DataFrame({
    "customer_id": [1, 1, 2, 1, 2, 3, 3, 1, 4, 2, 3],
    "created_at": pd.to_datetime([
        "2025-01-05 10:00", "2025-01-20 09:00", "2025-01-28 18:00",
        "2025-02-03 11:00", "2025-02-10 12:00", "2025-02-11 08:00",
        "2025-03-01 00:00", "2025-03-15 14:00", "2025-03-30 16:00", "2025-03-31 23:00",
        "2025-04-01 00:00"]),
})

quarter = jobs[(jobs["created_at"] >= "2025-01-01") & (jobs["created_at"] < "2025-04-01")]
per_month = quarter.groupby(quarter["created_at"].dt.month)["customer_id"].nunique()
print(per_month.tolist())
print(int(per_month.sum()))
print(int(quarter["customer_id"].nunique()))
print(len(quarter), len(jobs))
print(int(per_month.sum() - quarter["customer_id"].nunique()))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `s = pd.Series([1, 1, 2])` and a second group `t = pd.Series([2, 3])`, `s.nunique() + t.nunique()` is `4` but `pd.concat([s, t]).nunique()` is `3`: customer 2 is in both groups.

## After you answer

- Why is the sum of the monthly distinct counts bigger than the quarterly distinct count? Which customers are counted more than once?
- The job created at `2025-04-01 00:00` is in the table but not in the quarter. Which comparison operator keeps it out?
- When would summing distinct counts be correct?
