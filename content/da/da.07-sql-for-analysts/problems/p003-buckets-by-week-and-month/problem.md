# Buckets by week and month

Chapter section 2.4. To count things per week or per month, first map every timestamp to the **start of its bucket** with
`date_trunc('week', ts)` or `date_trunc('month', ts)`, then `GROUP BY` that value. In DuckDB a week starts on **Monday**
(`date_trunc('week', DATE '2025-01-01')` is the Monday `2024-12-30`).

```python
import duckdb, pandas as pd
con = duckdb.connect()
con.register("users", users)
# from solution import QUERY
print(con.execute(QUERY).df())
```

```python
users = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5, 6, 7],
    "signup_at": pd.to_datetime(["2024-12-31 09:00", "2025-01-01 10:00", "2025-01-05 23:59", "2025-01-06 00:00",
                                 "2025-01-31 12:00", "2025-02-01 08:00", "2025-02-10 15:30"]),
    "channel": ["organic", "ads", "ads", "referral", "organic", "ads", "organic"],
    "country": ["IN", "IN", "US", "UK", "US", "IN", "IN"]})
```

Return signups per week and per month **in one result**, with these columns:

| column | meaning |
|---|---|
| `period` | the text `'week'` or `'month'` |
| `period_start` | the first day of the bucket, as a date (`2024-12-30`, `2025-01-01`, ...) |
| `signups` | how many users signed up in that bucket |

A bucket with no signups does not need a row. Put the SQL in `QUERY` (hint: two `SELECT`s joined by `UNION ALL`).

## Example

User 1 signed up on 31 Dec 2024, a Tuesday: she is in the week starting `2024-12-30` and in the month starting `2024-12-01`.
User 3 (Sunday 5 Jan, 23:59) and user 4 (Monday 6 Jan, 00:00) are in **different** weeks even though one minute apart.
