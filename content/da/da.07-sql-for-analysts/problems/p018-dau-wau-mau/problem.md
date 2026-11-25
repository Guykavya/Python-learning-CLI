# DAU, WAU, MAU

Chapter section 5.2. "Active user" needs a definition: here, **a user with a `login` event**. Because users repeat, the counts are
**distinct** counts, and distinct counts are not additive: you cannot add seven daily counts to get the weekly one. A rolling
version asks, for each day `D`: how many *different* users were active on `D` (DAU), in the 7 days ending on `D` (WAU), in the
30 days ending on `D` (MAU)?

```python
import duckdb, pandas as pd
con = duckdb.connect()
con.register("events", events)
# from solution import QUERY
print(con.execute(QUERY).df())
```

```python
events = pd.DataFrame({
    "event_id": list(range(1, 9)),
    "user_id": [1, 1, 2, 3, 4, 4, 5, 2],
    "event_time": pd.to_datetime(["2025-06-01 09:00", "2025-06-02 09:00", "2025-06-01 10:00", "2025-06-08 11:00",
                                  "2025-06-08 12:00", "2025-06-09 08:00", "2025-07-05 10:00", "2025-06-08 13:00"]),
    "event_type": ["login", "login", "login", "login", "login", "login", "login", "view_course"]})
```

Build a calendar from the **first to the last login date** and return one row per day:

| column | meaning |
|---|---|
| `day` | the date |
| `dau` | distinct users with a login on `day` |
| `wau` | distinct users with a login in `day - 6` ... `day` (7 days, both ends included) |
| `mau` | distinct users with a login in `day - 29` ... `day` (30 days, both ends included) |

Days without any login still get a row (their counts may still be positive for `wau` and `mau`). Put the SQL in `QUERY`.

## Example

On 8 June, users 3 and 4 logged in (user 2's `view_course` is not a login): `dau = 2`. In the week 2 to 8 June the active users are 1 (2 June),
3 and 4: `wau = 3` (user 2 logged in on 1 June, one day too early). In the 30 days up to 8 June: users 1, 2, 3, 4: `mau = 4`.
