# Unordered or ordered funnel?

Chapter section 7.3. Two ways to say "reached step 3":

- **Unordered**: the user has a checkout event at all.
- **Ordered**: the user has a checkout event **on or after** their cart event, which is on or after their view.

The two differ when the data contain shortcuts (a direct purchase link with no earlier steps), tracking gaps or a purchase
that happened *before* the first view. Finance wants every buyer (unordered); the product team judging the page flow wants the
strict **ordered** funnel. In SQL, `t_cart >= t_view` is unknown when either side is `NULL`, so a user who skipped a step fails the
condition, which is what a strict funnel needs.

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
    "user_id": [1, 2, 3, 4, 5, 6],
    "signup_at": pd.to_datetime(["2025-03-01"] * 6),
    "channel": ["organic", "ads", "ads", "referral", "organic", "ads"],
    "country": ["IN", "IN", "US", "UK", "US", "IN"]})
events = pd.DataFrame({
    "event_id": list(range(1, 13)),
    "user_id": [1, 1, 1, 1, 2, 2, 3, 3, 4, 5, 3, 1],
    "event_time": pd.to_datetime(["2025-03-02 10:00", "2025-03-02 11:00", "2025-03-02 12:00", "2025-03-02 12:30",
                                  "2025-03-01 09:00", "2025-03-03 09:00", "2025-03-04 10:00", "2025-03-04 10:00",
                                  "2025-03-05 08:00", "2025-03-06 08:00", "2025-03-04 09:59", "2025-03-09 10:00"]),
    "event_type": ["view_course", "add_to_cart", "checkout_start", "purchase", "purchase", "view_course", "view_course", "add_to_cart",
                   "purchase", "view_course", "login", "login"]})
```

Build the **ordered funnel** (use the first time of each step per user, as in the previous problem) and return one row per step:

| column | meaning |
|---|---|
| `step` | 1 to 4 |
| `name` | `view_course`, `add_to_cart`, `checkout_start`, `purchase` |
| `users` | step 1: users with a view. Step 2: with a cart time **on or after** the view time. Step 3: also a checkout time on or after the cart time. Step 4: also a purchase time on or after the checkout time |

"On or after" means `>=`: two steps at exactly the same moment count as in order. Put the SQL in `QUERY`.

## Example

User 1 did all four steps in order. User 2 **purchased before viewing** (purchase on 1 March, view on 3 March): user 2 is in step 1 but
not in step 4. User 4 only has a purchase (a direct link): in no step of the ordered funnel. User 3 viewed and added to cart at the same moment: in step 2.
