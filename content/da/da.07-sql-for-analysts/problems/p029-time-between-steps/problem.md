# Time between steps

Chapter section 7.5. How long do users take from `add_to_cart` to `purchase`? Time data are skewed (a few users wait for days), so
use the **median**, not the mean. Remember what the number describes: only users who **did both** steps have a time. Users
who never bought have none, so the result is the median among **converters**, not among all users who added to the cart.

Use each user's **first** `add_to_cart` and **first** `purchase`. A user counts as a converter only when the first purchase
is **at or after** the first cart time (a purchase before the cart is a different story).

```python
import duckdb, pandas as pd
con = duckdb.connect()
con.register("users", users)
con.register("events", events)
# from solution import QUERY
print(con.execute(QUERY).df())
```

```python
users = pd.DataFrame({
    "user_id": list(range(1, 10)),
    "signup_at": pd.to_datetime(["2025-03-01"] * 9),
    "channel": ["ads", "ads", "ads", "organic", "organic", "ads", "organic", "referral", "ads"],
    "country": "IN"})
events = pd.DataFrame({
    "event_id": list(range(1, 15)),
    "user_id": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 8],
    "event_time": pd.to_datetime(["2025-03-02 10:00", "2025-03-02 15:00", "2025-03-03 08:00", "2025-03-03 11:00",
                                  "2025-03-04 09:00", "2025-03-04 19:00", "2025-03-05 10:00", "2025-03-05 12:00",
                                  "2025-03-06 10:00", "2025-03-06 14:00", "2025-03-07 10:00", "2025-03-07 08:00",
                                  "2025-03-08 10:00", "2025-03-09 10:00"]),
    "event_type": ["add_to_cart", "purchase", "add_to_cart", "purchase", "add_to_cart", "purchase", "add_to_cart", "purchase",
                   "add_to_cart", "purchase", "add_to_cart", "purchase", "add_to_cart", "purchase"]})
```

Return one row per channel that has at least one converter:

| column | meaning |
|---|---|
| `channel` | the channel |
| `converters` | users of the channel who carted and then purchased |
| `median_hours` | the median number of hours between the first cart time and the first purchase time, among those users |

Put the SQL in `QUERY`. Hours are fractional (`epoch(t2 - t1) / 3600.0`), not rounded.

## Example

Among `ads` users, user 1 took 5 hours (10:00 to 15:00), user 2 took 3 hours and user 3 took 10 hours: three converters, the median is
5. User 6 purchased **before** the cart (08:00 against 10:00) and is not a converter. `referral` has no converter: no row.
