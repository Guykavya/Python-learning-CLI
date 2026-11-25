# Business questions answered in SQL

Chapter section 11, the module project. LearnLoop's leadership asks five questions. Answer each with **one SQL query**, keep
them in a dictionary so a single loop can run, check and save them, and put the **definition at the top of each query as a
comment** (as you practised in da.06). Your queries run on the three LearnLoop tables (`users`, `events`, `orders`; the data
end on 2025-07-15) and the test checks every one against an independent pandas computation, and checks the **grain**
(one row per stated key).

Write, in `solution.py`, a dictionary `QUERIES` with exactly these five keys (the values are SQL strings; each string must
**start with a `--` comment** that states the definition):

**1. `monthly_revenue_growth`**: columns `month, revenue, prev_revenue, growth_pct`; key `month`.
Revenue is the sum of `amount` by month of `order_time`, for **complete months** (only orders before `2025-07-01`), for **every month
from the first to the last order month** (a month without orders has revenue 0). `prev_revenue` is the previous month's revenue (`NULL`
for the first month), `growth_pct = (revenue - prev_revenue) * 100 / prev_revenue`, `NULL` when `prev_revenue` is `NULL` or 0.

**2. `retention_grid`**: columns `cohort, month_number, active_users, cohort_size, retention`; key `cohort, month_number`.
Cohort = month of `signup_at`; active = a `login` in the calendar month; one row for each cohort and each `month_number` 0 to 5.
A cell is observed only when the month `cohort + month_number` is complete (before `2025-07-01`): then `active_users` is a count (0 allowed);
otherwise `active_users` and `retention` are `NULL` (not 0). `retention = active_users / cohort_size`.

**3. `ordered_funnel_by_channel`**: columns `channel, viewed, carted, checkout, purchased`; key `channel`.
Per user, the first time of each step; a user counts for a step when that step is **on or after** the previous one, all the way back to the
view (the ordered funnel of problem 28). One row for every channel of `users`.

**4. `top2_spenders_per_country`**: columns `country, user_id, spent, rank_in_country`; key `country, rank_in_country`.
`spent` is the sum of the user's order amounts; the two biggest spenders of each country, ties broken by the smaller `user_id`;
`rank_in_country` is 1 or 2. (The LearnLoop tables have no course column, so we rank users, as in the chapter.)

**5. `active_user_states`**: columns `month, mau, new_users, retained, resurrected, churned`; key `month`.
Active = a `login` in the month, complete months only (before `2025-07-01`). `mau` = active users; `new_users` = first active month;
`retained` = also active the previous calendar month; `resurrected` = active, not the previous month, but earlier; `churned` =
MAU of the previous month minus `retained` (`NULL` for the first month).

```python
import duckdb
con = duckdb.connect()
# register users, events, orders as in the chapter (Ch. 1.2), then:
# from solution import QUERIES
# for name, sql in QUERIES.items():
#     print(name, con.execute(sql).df().shape)
```

## Example

`QUERIES["top2_spenders_per_country"]` returns at most two rows per country. If user 7 and user 9 of country `IN` both spent 3999, user 7
is rank 1 (smaller id).
