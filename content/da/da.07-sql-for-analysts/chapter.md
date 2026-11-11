# Chapter 7 (DA): SQL for analysts

In shared.01 you learned SQL as a language: `SELECT`, `JOIN`, `GROUP BY`, `NULL`, a first look at window functions. This chapter uses SQL the way analysts do every day. The questions are no longer "list the rows where..." but "of the users who signed up in March, how many were still active ten weeks later?", "where do people drop out of the buying process?", "what is the 7-day moving average of daily users?". These questions need three things: **window functions** (calculations across related rows without collapsing them), **careful definitions** (you learned that in da.06), and **patterns** (cohort, funnel, retention) that you can copy from one project to the next.

By the end of this chapter you reach one outcome: **you can build a cohort retention table in SQL**, correctly, including the part most people get wrong (cohorts that have not had time to reach a given month). On the way you will meet the engine we use, **DuckDB**, an analytical database that runs inside Python with no server and that can query pandas DataFrames and Parquet files directly.

Prerequisites: shared.01 (SQL foundations: joins, aggregation, subqueries, CTEs, a first window function), da.04 (groupby, merge) and da.06 (grain, fan-out, metric definitions). The ideas of da.06 return all the time: before a query, say what one row is; after a join, compare counts; write the definition of the metric in a comment.

> **Offline rule for this chapter.** DuckDB, pandas, NumPy and PyArrow are installed in the course environment. No internet and no database server are needed. Every dataset is **synthetic**: built in code with seeded random numbers, so you get the same numbers I did. The app, its users and its prices are invented; the *structure* (users, an event log, orders) is the structure of real product data. Files are written only into a temporary folder. Every output block below was produced by running the code above it, in one session from top to bottom. **Timings, versions and temporary paths are machine-specific.** Some blocks show an error on purpose; for errors we print only the last line. These are the versions used:

```python run
import sys, platform
import numpy as np
import pandas as pd
import duckdb

print("python ", sys.version.split()[0])
print("pandas ", pd.__version__)
print("numpy  ", np.__version__)
print("duckdb ", duckdb.__version__)
```
```text
python  3.14.4
pandas  3.1.1
numpy   2.5.4
duckdb  2.0.0
```

Two setup lines make the printed tables compact.

```python run
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 14)
pd.set_option("display.max_rows", 20)
pd.set_option("display.float_format", "{:,.2f}".format)
print("display options set")
```
```text
display options set
```

## Table of contents

1. [DuckDB and the dataset](#1-duckdb-and-the-dataset)
2. [Analytical SQL patterns](#2-analytical-sql-patterns)
3. [CTEs: queries that read like a recipe](#3-ctes-queries-that-read-like-a-recipe)
4. [Window functions in depth](#4-window-functions-in-depth)
5. [Calendars and dates](#5-calendars-and-dates)
6. [Cohort retention](#6-cohort-retention)
7. [Funnels](#7-funnels)
8. [Who is active: new, retained, resurrected, churned](#8-who-is-active-new-retained-resurrected-churned)
9. [DuckDB with pandas and Parquet](#9-duckdb-with-pandas-and-parquet)
10. [Checking your SQL](#10-checking-your-sql)
11. [Project: business questions answered in SQL](#11-project-business-questions-answered-in-sql)
12. [Common traps](#12-common-traps)
13. [Summary](#13-summary)

## 1. DuckDB and the dataset

### 1.1 Why DuckDB

Analysts need an engine that is **fast on aggregations**, runs on a laptop, and speaks full SQL. DuckDB is a database that lives inside your Python process, like `sqlite3`. The difference is the design goal. SQLite stores data by row and is built for many small reads and writes (an app). DuckDB stores data by **column** and is built for scanning millions of rows and aggregating them (analysis). It reads pandas DataFrames, CSV files and Parquet files directly, and it supports modern SQL features that make analytic queries shorter: `QUALIFY`, `GROUP BY ALL`, `FILTER`, `PIVOT`, and a long list of date and list functions.

You connect to it in one line. An in-memory database disappears when the program ends, which is what we want for learning.

```python run
con = duckdb.connect()                                   # an in-memory database

def q(sql, *params):
    """Run a query and return a pandas DataFrame."""
    return con.execute(sql, list(params)).df()


print(q("SELECT 40 + 2 AS answer, 'hello' AS word, current_date IS NOT NULL AS has_date"))
```
```text
   answer   word  has_date
0      42  hello      True
```

`con.execute(sql, [params])` runs a query with `?` placeholders (never build SQL by pasting values into text: it is the SQL-injection mistake you met in swe.03). `.df()` returns the result as a DataFrame.

### 1.2 The dataset: LearnLoop

Our synthetic company is **LearnLoop**, an online-course app. A user **signs up**, **logs in** on some days, **browses** a course, **adds it to the cart**, **starts checkout** and **purchases** a plan. Three tables describe it:

| Table | One row is... | Key |
|---|---|---|
| `users` | one user | `user_id` |
| `events` | one event: something a user did at a moment | (`user_id`, `event_time`, `event_type`) is *not* guaranteed unique |
| `orders` | one purchase | `order_id` |

The data run from 1 January 2025 to the extraction on **15 July 2025**. Users signed up between January and June, so older cohorts have had much more time than newer ones. That fact will matter a lot in section 6. Timestamps are plain UTC without a time zone; to keep this chapter about SQL we do not convert them (you practised that in da.06).

```python run
END = pd.Timestamp("2025-07-15")                  # extraction time: nothing after this exists


def make_app(seed=8, n=4000):
    rng = np.random.default_rng(seed)
    signup = pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 181 * 24 * 60, n), unit="min")
    users = pd.DataFrame({"user_id": np.arange(1, n + 1), "signup_at": signup,
                          "channel": rng.choice(["organic", "ads", "referral"], n, p=[.5, .35, .15]),
                          "country": rng.choice(["IN", "US", "UK"], n, p=[.6, .25, .15])})
    # ---- logins: each user stays "engaged" for a random time, then drifts away; referral users stay longer
    life_scale = users["channel"].map({"organic": 60, "ads": 25, "referral": 120}).to_numpy()   # mean days engaged
    daily_p = users["channel"].map({"organic": .30, "ads": .25, "referral": .40}).to_numpy()     # login chance per engaged day
    frames = []
    for uid, s, life_mean, dp in zip(users["user_id"], users["signup_at"], life_scale, daily_p):
        days = (END.normalize() - s.normalize()).days
        d = np.arange(0, days + 1)
        p = np.where(d <= rng.exponential(life_mean), dp, .01)   # after the engaged period only a rare visit
        p[0] = 1.0                                           # the signup day counts as a login
        hit = d[rng.random(len(d)) < p]
        t = s.normalize() + pd.to_timedelta(hit, unit="D") + pd.to_timedelta(rng.integers(6 * 60, 23 * 60, len(hit)), unit="min")
        t = t.where(hit > 0, s)                              # first login = the signup moment
        frames.append(pd.DataFrame({"user_id": uid, "event_time": t, "event_type": "login"}))
    # ---- buying funnel: view -> add_to_cart -> checkout_start -> purchase
    cart_p = {"organic": .40, "ads": .30, "referral": .50}
    rows = []
    for uid, s, ch in zip(users["user_id"], users["signup_at"], users["channel"]):
        if rng.random() < .03:                               # direct purchase link: no earlier steps (a data quirk)
            rows.append((uid, s + pd.Timedelta(days=int(rng.integers(0, 20))), "purchase"))
            continue
        if rng.random() < .85:
            t = s + pd.Timedelta(minutes=int(rng.integers(1, 3 * 24 * 60)))
            for k in range(int(rng.integers(1, 5))):         # a user may view several times
                rows.append((uid, t + pd.Timedelta(minutes=30 * k), "view_course"))
            if rng.random() < cart_p[ch]:
                t += pd.Timedelta(hours=float(rng.exponential(20)))
                rows.append((uid, t, "add_to_cart"))
                if rng.random() < .6:
                    t += pd.Timedelta(hours=float(rng.exponential(10)))
                    rows.append((uid, t, "checkout_start"))
                    if rng.random() < .65:
                        t += pd.Timedelta(minutes=float(rng.exponential(30)))
                        rows.append((uid, t, "purchase"))
                        if rng.random() < .10:               # a renewal: a second purchase later
                            rows.append((uid, t + pd.Timedelta(days=int(rng.integers(30, 60))), "purchase"))
    funnel = pd.DataFrame(rows, columns=["user_id", "event_time", "event_type"])
    events = pd.concat(frames + [funnel], ignore_index=True)
    events = events[events["event_time"] <= END].sort_values(["event_time", "user_id"]).reset_index(drop=True)
    events.insert(0, "event_id", np.arange(1, len(events) + 1))
    # ---- orders: one row per purchase event
    buys = events[events["event_type"] == "purchase"].reset_index(drop=True)
    plan = rng.choice(["monthly", "annual"], len(buys), p=[.7, .3])
    orders = pd.DataFrame({"order_id": 9001 + np.arange(len(buys)), "user_id": buys["user_id"], "order_time": buys["event_time"],
                           "plan": plan, "amount": np.where(plan == "monthly", 499, 3999)})
    return users, events, orders


users, events, orders = make_app()
for name, t in [("users", users), ("events", events), ("orders", orders)]:
    print(f"{name:7} {t.shape}")
print(events["event_type"].value_counts().to_string())
```
```text
users   (4000, 4)
events  (67421, 4)
orders  (697, 5)
event_type
login             56312
view_course        8302
add_to_cart        1312
checkout_start      798
purchase            697
```

DuckDB can read a pandas DataFrame **by its Python variable name**, with no loading step. The DataFrame must be visible in the program where you run the query (a "replacement scan"). To make this explicit and safe in a long program, we also register the three tables in our connection with names:

```python run
for name, t in [("users", users), ("events", events), ("orders", orders)]:
    con.register(name, t)
print(q("SHOW TABLES").to_string(index=False))
print(q("SELECT * FROM events ORDER BY event_id LIMIT 4").to_string(index=False))
```
```text
  name
events
orders
 users
 event_id  user_id          event_time  event_type
        1     2804 2025-01-01 00:35:00       login
        2     1939 2025-01-01 01:55:00       login
        3     1939 2025-01-01 02:19:00 view_course
        4     1789 2025-01-01 02:41:00       login
```

`register` makes a *view* of the DataFrame; nothing is copied. If you change the DataFrame, the query sees the change.

### 1.3 Grain, again

Before the first real query, state the grain of each table and test it, as in da.06.

```python run
print(q("""
SELECT 'users'  AS tbl, COUNT(*) AS rows_, COUNT(DISTINCT user_id)  AS keys FROM users
UNION ALL SELECT 'orders', COUNT(*), COUNT(DISTINCT order_id) FROM orders
UNION ALL SELECT 'events', COUNT(*), COUNT(DISTINCT event_id) FROM events
""").to_string(index=False))
print()
print("orders per user (users with at least one order):")
print(q("SELECT n_orders, COUNT(*) AS users FROM (SELECT user_id, COUNT(*) AS n_orders FROM orders GROUP BY user_id) GROUP BY n_orders ORDER BY n_orders").to_string(index=False))
```
```text
   tbl  rows_  keys
 users   4000  4000
orders    697   697
events  67421 67421

orders per user (users with at least one order):
 n_orders  users
        1    625
        2     36
```

`users` and `orders` have one row per key. `events` has a row per event, and one user has many events: counting rows in `events` counts events, not users. Some users have two orders (the renewals). That means "number of orders" and "number of buyers" differ, and the difference shows up in every funnel and revenue query.

> **Predict the output.** There are about 56,000 `login` events for 4,000 users, but only 697 purchases. If a manager asks "how many users logged in during June?", which of these queries is right: `COUNT(*)` of June login events, or `COUNT(DISTINCT user_id)`?

<details><summary>Answer</summary>

```python run
print(q("""
SELECT COUNT(*) AS login_events, COUNT(DISTINCT user_id) AS users
FROM events
WHERE event_type = 'login' AND event_time >= '2025-06-01' AND event_time < '2025-07-01'
""").to_string(index=False))
```
```text
 login_events  users
        11988   2291
```

`COUNT(DISTINCT user_id)` answers "how many users", and the number is much smaller than the event count because most users log in several times a month. `COUNT(*)` answers "how many login events". The question asked for users. The grain rule of da.06 applies in SQL word for word: **count the entity that the question names.**

</details>

## 2. Analytical SQL patterns

Analytic queries repeat a few moves. We collect them here, using DuckDB's syntax, and note where the same idea is written differently elsewhere.

### 2.1 Conditional aggregation

Instead of several queries (one for each condition), compute many measures in one pass with `CASE` inside an aggregate, or with the `FILTER` clause.

```python run
print(q("""
SELECT channel,
       COUNT(*)                                          AS users,
       COUNT(*) FILTER (WHERE country = 'IN')            AS users_in,
       ROUND(AVG(CASE WHEN country = 'IN' THEN 1.0 ELSE 0 END) * 100, 1) AS pct_in
FROM users
GROUP BY channel
ORDER BY users DESC
""").to_string(index=False))
```
```text
 channel  users  users_in  pct_in
 organic   1976      1141   57.70
     ads   1427       858   60.10
referral    597       364   61.00
```

`COUNT(*) FILTER (WHERE ...)` is the readable form; `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` is the portable form that works in every database. The average of a 0/1 flag is a **percentage**: a very common trick for rates.

### 2.2 Safe division and `NULL`

A rate divides by a count that may be zero. `NULLIF(x, 0)` turns a zero into `NULL`, so the division gives `NULL` (unknown) instead of an error or a wrong number. `COALESCE(x, default)` replaces `NULL` for display.

```python run
print(q("""
SELECT 5 / NULLIF(0, 0) AS safe_division,
       COALESCE(5 / NULLIF(0, 0), 0) AS shown_as_zero,
       7 / 2 AS integer_looking_division,
       7 // 2 AS floor_division
"""). to_string(index=False))
```
```text
 safe_division  shown_as_zero  integer_looking_division  floor_division
           NaN           0.00                      3.50               3
```

Careful with the division operator: in DuckDB `7 / 2` is `3.5` (true division), while in PostgreSQL, SQLite and MySQL (older versions) integer division gives `3`. Whenever you compute a ratio, check what your database does with two integers; multiply by `1.0` to be safe everywhere.

### 2.3 `GROUP BY ALL` and `SELECT * EXCLUDE`

Two DuckDB conveniences that keep queries short. `GROUP BY ALL` groups by every non-aggregated column in the `SELECT` list. `* EXCLUDE (col)` selects all columns but some.

```python run
print(q("""
SELECT channel, country, COUNT(*) AS users
FROM users
GROUP BY ALL
ORDER BY channel, country
LIMIT 4
""").to_string(index=False))
print(q("SELECT * EXCLUDE (signup_at, country) FROM users LIMIT 2").to_string(index=False))
```
```text
channel country  users
    ads      IN    858
    ads      UK    227
    ads      US    342
organic      IN   1141
 user_id channel
       1 organic
       2 organic
```

Use `GROUP BY ALL` for exploration. In long, shared queries, explicit column names (or numbers) make the grain visible, so be careful: with `GROUP BY ALL` it is easy to add a column to the `SELECT` and silently change the grain of the result.

### 2.4 Dates and buckets

`date_trunc(unit, t)` cuts a timestamp down to the start of the unit (day, week, month). `date_diff(unit, a, b)` counts the unit boundaries crossed between `a` and `b`.

```python run
print(q("""
SELECT date_trunc('month', signup_at)::DATE AS month,
       COUNT(*) AS signups
FROM users
GROUP BY 1
ORDER BY 1
""").to_string(index=False))
print(q("SELECT date_trunc('week', DATE '2025-03-05') AS week_start, dayname(date_trunc('week', DATE '2025-03-05')) AS weekday").to_string(index=False))
```
```text
     month  signups
2025-01-01      644
2025-02-01      618
2025-03-01      730
2025-04-01      684
2025-05-01      709
2025-06-01      615
week_start weekday
2025-03-03  Monday
```

A week starts on Monday in DuckDB (and PostgreSQL); in some tools it starts on Sunday. State the convention. `date_diff('month', DATE '2025-01-31', DATE '2025-02-01')` gives 1 although only one day passed: it counts **boundaries**, not elapsed time. That distinction is the source of several off-by-one mistakes in retention queries (section 6).

```python run
print(q("""
SELECT date_diff('month', DATE '2025-01-31', DATE '2025-02-01') AS months_by_boundary,
       date_diff('day',   DATE '2025-01-31', DATE '2025-02-01') AS days_between,
       date_sub('month', DATE '2025-01-31', DATE '2025-02-01') AS full_months_elapsed
""").to_string(index=False))
```
```text
 months_by_boundary  days_between  full_months_elapsed
                  1             1                    0
```

`date_sub` counts only *complete* units: 0 full months have passed. Which of the two you need depends on the definition of your metric: "the calendar month after signup" uses `date_diff`, "30 days after signup" uses days.

### 2.5 Dialect notes

You will write SQL on more than one engine in your career. The ideas are the same; the spelling differs.

| Idea | DuckDB | PostgreSQL | SQLite |
|---|---|---|---|
| Start of month | `date_trunc('month', t)` | `date_trunc('month', t)` | `date(t, 'start of month')` |
| Days between | `date_diff('day', a, b)` | `b::date - a::date` | `julianday(b) - julianday(a)` |
| Filter on a window result | `QUALIFY` | subquery or CTE | subquery or CTE |
| Calendar of dates | `generate_series(d1, d2, INTERVAL 1 DAY)` | `generate_series(d1, d2, '1 day')` | recursive CTE |
| Conditional count | `COUNT(*) FILTER (WHERE c)` | `COUNT(*) FILTER (WHERE c)` | `SUM(CASE ...)` |
| Median | `median(x)` | `percentile_cont(0.5) WITHIN GROUP (ORDER BY x)` | not built in |

When you must write portable code, stay with `CASE`, `COALESCE`, CTEs, standard window functions, and put the dialect-specific date handling in one place.

## 3. CTEs: queries that read like a recipe

### 3.1 The pattern

A **CTE** (common table expression, the `WITH name AS (...)` clause) gives a name to an intermediate result. A long query becomes a short recipe: one named step per idea, each with one clear grain. Compare "how many users logged in each month, and what share of all users is that?" written in two ways.

```python run
print(q("""
WITH monthly_users AS (          -- grain: one row per month
  SELECT date_trunc('month', event_time)::DATE AS month,
         COUNT(DISTINCT user_id) AS active_users
  FROM events
  WHERE event_type = 'login'
  GROUP BY 1
),
totals AS (                      -- grain: one row, the number of users who exist
  SELECT COUNT(*) AS all_users FROM users
)
SELECT m.month, m.active_users, t.all_users,
       ROUND(m.active_users * 100.0 / t.all_users, 1) AS pct_of_all_users
FROM monthly_users m CROSS JOIN totals t
ORDER BY m.month
""").to_string(index=False))
```
```text
     month  active_users  all_users  pct_of_all_users
2025-01-01           644       4000             16.10
2025-02-01          1127       4000             28.20
2025-03-01          1564       4000             39.10
2025-04-01          1828       4000             45.70
2025-05-01          2167       4000             54.20
2025-06-01          2291       4000             57.30
2025-07-01          1472       4000             36.80
```

Each CTE carries a comment with its **grain**. The final `SELECT` only joins and formats. If the numbers look wrong, you can run each CTE alone and look at it: this is the debugging method of SQL.

Look at the denominator: `all_users` is all 4,000 users **ever created**, including those who had not signed up yet in January. A reader who sees "active 16.1 percent in January" might think the denominator is the users that existed in January. As in da.06, the name of the percentage must say what the denominator is. A more careful query uses only the users who existed at the end of each month:

```python run
print(q("""
WITH months AS (SELECT DISTINCT date_trunc('month', signup_at)::DATE AS month FROM users),
exists_by_month AS (             -- grain: one row per month: users who had signed up by the month's end
  SELECT m.month, COUNT(u.user_id) AS users_existing
  FROM months m LEFT JOIN users u ON u.signup_at < m.month + INTERVAL 1 MONTH
  GROUP BY m.month),
active AS (                      -- grain: one row per month
  SELECT date_trunc('month', event_time)::DATE AS month, COUNT(DISTINCT user_id) AS active_users
  FROM events WHERE event_type = 'login' GROUP BY 1)
SELECT e.month, e.users_existing, a.active_users, ROUND(a.active_users * 100.0 / e.users_existing, 1) AS pct_active
FROM exists_by_month e JOIN active a USING (month) ORDER BY e.month
""").to_string(index=False))
```
```text
     month  users_existing  active_users  pct_active
2025-01-01             644           644      100.00
2025-02-01            1262          1127       89.30
2025-03-01            1992          1564       78.50
2025-04-01            2676          1828       68.30
2025-05-01            3385          2167       64.00
2025-06-01            4000          2291       57.30
```

Now the denominators grow month by month, and the active share is much higher. The first version divided by a number that included people who did not yet exist; its percentages were too small, most of all for January. That is a **denominator error**, and no SQL error message will warn you. (One more detail: July is missing from the second table, because the list of months came from the *signup* months. The first query, built from the events, shows July. Where a list of periods comes from is a decision, too.)

### 3.2 CTE rules of thumb

1. **One idea per CTE**, named for what it contains (`first_login`, `cohort_size`), not for how it is built (`temp1`).
2. **Write the grain in a comment** on the first line of each CTE.
3. **Filter early**, aggregate before joining (da.06): put `WHERE` conditions in the first CTE that touches the big table.
4. **Do not repeat a subquery.** If the same expression appears twice, make it a CTE.
5. **Check each CTE's row count** while you build, as you checked merges in pandas.

CTEs are not a performance trick (the optimiser usually treats them like subqueries). They are a **readability** tool. For intermediate results used by several queries, a view or a table is better.


## 4. Window functions in depth

### 4.1 The idea

An aggregate with `GROUP BY` **collapses** rows: 100 orders become 4 rows, one per plan. A **window function** computes across a set of related rows and **keeps every row**. The extra column answers a question such as "what is this row's rank among its group?", "what was the previous value?", "what is the total so far?".

```text
function(...) OVER (
    PARTITION BY ...     -- which rows belong together (like GROUP BY, but rows stay)
    ORDER BY ...         -- in which order inside the partition
    ROWS / RANGE ...     -- which neighbouring rows are included (the frame)
)
```

Every part after `OVER (` is optional. Start with an example that shows the difference: each order, together with the user's order count and the user's total spent.

```python run
print(q("""
SELECT order_id, user_id, order_time::DATE AS day, amount,
       COUNT(*)    OVER (PARTITION BY user_id) AS orders_of_user,
       SUM(amount) OVER (PARTITION BY user_id) AS spent_by_user
FROM orders
WHERE user_id IN (SELECT user_id FROM orders GROUP BY user_id HAVING COUNT(*) = 2 LIMIT 2)
ORDER BY user_id, order_time
""").to_string(index=False))
```
```text
 order_id  user_id        day  amount  orders_of_user  spent_by_user
     9395      179 2025-04-15     499               2         998.00
     9555      179 2025-05-25     499               2         998.00
     9465     3167 2025-05-03    3999               2       4,498.00
     9657     3167 2025-06-21     499               2       4,498.00
```

Four rows came in, four rows came out. `COUNT(*) OVER (PARTITION BY user_id)` repeated the user's count on every row of that user. This is the same "value repeated at a finer grain" that caused fan-out in da.06, but now on purpose: you know the new column has the user's grain. **The grain of a window column is the partition.** If you now sum `spent_by_user` over all rows, you double-count; that is the same mistake in a new form.

### 4.2 Ranking: `row_number`, `rank`, `dense_rank`, `ntile`

Four functions number the rows of a partition. They differ only when there are **ties**.

```python run
print(q("""
SELECT name, score,
       row_number() OVER (ORDER BY score DESC) AS row_number,
       rank()       OVER (ORDER BY score DESC) AS rank,
       dense_rank() OVER (ORDER BY score DESC) AS dense_rank,
       ntile(2)     OVER (ORDER BY score DESC) AS half
FROM (VALUES ('Asha', 90), ('Ravi', 85), ('Meera', 85), ('Dev', 70), ('Isha', 60)) AS t(name, score)
ORDER BY score DESC, name
""").to_string(index=False))
```
```text
 name  score  row_number  rank  dense_rank  half
 Asha     90           1     1           1     1
Meera     85           3     2           2     1
 Ravi     85           2     2           2     1
  Dev     70           4     4           3     2
 Isha     60           5     5           4     2
```

| Function | Ties | Next number after a tie of two | Use it for |
|---|---|---|---|
| `row_number` | broken **arbitrarily** | no gap | "the first row", de-duplication |
| `rank` | same number | skips (1, 2, 2, **4**) | competition ranking |
| `dense_rank` | same number | no skip (1, 2, 2, **3**) | "the second-highest value" |
| `ntile(n)` | -- | -- | split into `n` equal buckets (quartiles) |

Watch `row_number` with ties: Ravi and Meera have the same score, and the database may number them either way. If a query must be reproducible, add a **tie-breaker** to `ORDER BY` (`ORDER BY score DESC, name`).

### 4.3 Looking at neighbours: `lag`, `lead`, `first_value`

`lag(x, n)` gives the value from `n` rows **before** in the partition order, `lead(x, n)` from `n` rows after. They are the SQL form of `groupby().shift()` in pandas. The first row of a partition has no previous row, so `lag` returns `NULL` (or a default you pass).

```python run
print(q("""
WITH l AS (
  SELECT user_id, event_time
  FROM events WHERE event_type = 'login' AND user_id = 2
)
SELECT user_id, event_time::DATE AS login_day,
       lag(event_time::DATE)  OVER w AS previous_login,
       date_diff('day', lag(event_time::DATE) OVER w, event_time::DATE) AS days_since_previous,
       first_value(event_time::DATE) OVER w AS first_login
FROM l
WINDOW w AS (PARTITION BY user_id ORDER BY event_time)
ORDER BY event_time
LIMIT 6
""").to_string(index=False))
```
```text
 user_id  login_day previous_login  days_since_previous first_login
       2 2025-03-01            NaT                 <NA>  2025-03-01
       2 2025-03-03     2025-03-01                    2  2025-03-01
       2 2025-03-05     2025-03-03                    2  2025-03-01
       2 2025-03-07     2025-03-05                    2  2025-03-01
       2 2025-03-08     2025-03-07                    1  2025-03-01
       2 2025-03-15     2025-03-08                    7  2025-03-01
```

The `WINDOW w AS (...)` clause names a window, so you write it once and reuse it. The first row has `NULL` for the previous login, and the gap to it is `NULL` too: "no previous login" is not "zero days". Now use the gap to answer a question: how long do users stay away between logins?

```python run
print(q("""
WITH gaps AS (
  SELECT user_id,
         date_diff('day', lag(event_time::DATE) OVER (PARTITION BY user_id ORDER BY event_time), event_time::DATE) AS gap_days
  FROM events WHERE event_type = 'login'
)
SELECT COUNT(gap_days) AS gaps, ROUND(AVG(gap_days), 2) AS mean_gap, median(gap_days) AS median_gap,
       quantile_cont(gap_days, 0.9) AS p90_gap, MAX(gap_days) AS longest_gap
FROM gaps
""").to_string(index=False))
```
```text
 gaps  mean_gap  median_gap  p90_gap  longest_gap
52312      4.88        2.00     8.00          188
```

`COUNT(gap_days)` counts only non-null gaps (the first login of each user has none), and the mean is much higher than the median: a few long absences pull it up. As in da.06, the right summary of a skewed gap is the median and a high percentile, not the mean alone.

### 4.4 Frames: which rows are inside the window?

When you add `ORDER BY` to an aggregate window, the **frame** decides which rows are summed. This is where most window-function bugs hide. The default frame, when there is an `ORDER BY`, is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`: from the start of the partition to the current row **and every row tied with it** (the "peers").

```python run
print(q("""
SELECT day, amount,
       SUM(amount) OVER (ORDER BY day)                                              AS default_frame,
       SUM(amount) OVER (ORDER BY day, amount ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS rows_frame
FROM (VALUES (DATE '2025-03-01', 10), (DATE '2025-03-02', 20), (DATE '2025-03-02', 5), (DATE '2025-03-03', 15)) AS t(day, amount)
ORDER BY day, amount
""").to_string(index=False))
```
```text
       day  amount  default_frame  rows_frame
2025-03-01      10          10.00       10.00
2025-03-02       5          35.00       15.00
2025-03-02      20          35.00       35.00
2025-03-03      15          50.00       50.00
```

The two middle rows share the date 2 March. With the **default** (`RANGE`) frame, both see 35 (10 + 20 + 5), because tied rows are peers and are included together: the running total jumps by 25 and there is no row where it shows 30. With a **`ROWS`** frame, each row is added one at a time (15, then 35). Note that we gave the `ROWS` window a tie-breaker (`ORDER BY day, amount`): without one, the database may add the two tied rows in either order, and the first would show 30 or 15 depending on the run. Neither is "wrong", but they answer different questions. For a running total over rows, write `ROWS` explicitly. For a running total over days, first aggregate to one row per day, then it does not matter.

The three kinds of frame:

| Frame | Counts | Example |
|---|---|---|
| `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` | a number of **rows** | the last 7 rows |
| `RANGE BETWEEN INTERVAL 6 DAY PRECEDING AND CURRENT ROW` | a **value distance** on the ordering column | the last 7 days, whatever the number of rows |
| `GROUPS BETWEEN 1 PRECEDING AND CURRENT ROW` | a number of **peer groups** | this and the previous distinct day |

A second frame trap: `last_value(x) OVER (ORDER BY t)` with the default frame returns the **current** row's value (the frame ends at the current row), not the last of the partition. To get the true last value, extend the frame to the end:

```python run
print(q("""
SELECT day, amount,
       last_value(amount) OVER (ORDER BY day)                                                       AS last_default,
       last_value(amount) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_true
FROM (VALUES (DATE '2025-03-01', 10), (DATE '2025-03-02', 20), (DATE '2025-03-03', 15)) AS t(day, amount)
ORDER BY day
""").to_string(index=False))
```
```text
       day  amount  last_default  last_true
2025-03-01      10            10         15
2025-03-02      20            20         15
2025-03-03      15            15         15
```

### 4.5 Running totals and moving averages

Daily revenue is the base for both. But look at the trap first: days with no orders do not appear in the table, so "the last 7 rows" is not "the last 7 days".

```python run
print(q("""
WITH daily AS (                       -- grain: one row per day that HAS orders
  SELECT order_time::DATE AS day, SUM(amount) AS revenue, COUNT(*) AS orders
  FROM orders GROUP BY 1
)
SELECT day, revenue,
       SUM(revenue) OVER (ORDER BY day ROWS UNBOUNDED PRECEDING) AS running_total,
       ROUND(AVG(revenue) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 0) AS avg_last_7_rows,
       ROUND(AVG(revenue) OVER (ORDER BY day RANGE BETWEEN INTERVAL 6 DAY PRECEDING AND CURRENT ROW), 0) AS avg_last_7_days
FROM daily
QUALIFY avg_last_7_rows <> avg_last_7_days
ORDER BY day
LIMIT 4
""").to_string(index=False))
print(q("SELECT COUNT(DISTINCT order_time::DATE) AS days_with_orders, DATE '2025-07-15' - MIN(order_time::DATE) + 1 AS days_in_period FROM orders").to_string(index=False))
```
```text
       day   revenue  running_total  avg_last_7_rows  avg_last_7_days
2025-03-22  9,495.00     391,713.00         7,425.00         8,496.00
2025-03-23 17,992.00     409,705.00         9,852.00         9,995.00
2025-03-24    998.00     410,703.00         8,710.00         7,829.00
2025-03-25  5,496.00     416,199.00         7,496.00         7,246.00
 days_with_orders  days_in_period
              185             194
```

The output shows only the days where the two averages **disagree**: they are the days right after a day without orders, where "the last 7 rows" reaches back more than 7 days. Between the first order (3 January) and 15 July there are 194 days; 185 have orders and 9 do not.

The `RANGE ... INTERVAL 6 DAY` frame averages over the last 7 *calendar days that have a row*, and `ROWS` averages over the last 7 rows, which can cover far more than 7 days when some days are empty. Both skip the empty days; a moving average that should treat an empty day as **zero revenue** needs a calendar with a row for every day. That is section 5.

### 4.6 Share of the total, and the cumulative share

`SUM(x) OVER ()` with an empty window is the total of the whole result. Dividing by it gives each row's share, without a join.

```python run
print(q("""
WITH by_user AS (                           -- grain: one row per user who bought
  SELECT user_id, SUM(amount) AS spent FROM orders GROUP BY 1
),
ranked AS (
  SELECT user_id, spent,
         ROUND(spent * 100.0 / SUM(spent) OVER (), 3)                                     AS pct_of_revenue,
         ROUND(SUM(spent) OVER (ORDER BY spent DESC, user_id ROWS UNBOUNDED PRECEDING) * 100.0 / SUM(spent) OVER (), 1) AS cumulative_pct,
         row_number() OVER (ORDER BY spent DESC, user_id) AS rn
  FROM by_user
)
SELECT * FROM ranked WHERE rn IN (1, 10, 50, 100, 200, 400, 661) ORDER BY rn
""").to_string(index=False))
```
```text
 user_id    spent  pct_of_revenue  cumulative_pct  rn
     970 7,998.00            0.77            0.80   1
    1858 4,498.00            0.43            6.40  10
     681 3,999.00            0.39           22.30  50
    2094 3,999.00            0.39           41.60 100
    1812   998.00            0.10           77.50 200
    1859   499.00            0.05           87.40 400
    3992   499.00            0.05          100.00 661
```

The `cumulative_pct` column is the data of a Pareto curve: the best 50 buyers account for the share shown. The pattern `SUM(...) OVER (ORDER BY ... ROWS UNBOUNDED PRECEDING) / SUM(...) OVER ()` gives a cumulative share in one query. Note the tie-breaker `user_id`: buyers who spent exactly the same amount need an unambiguous order, or the numbers may change between runs.

### 4.7 Top N per group and "the latest row"

"The first purchase of each user", "the latest login per user", "the top 3 orders per country" all need a **rank inside a group**, then a filter on the rank. In most databases that takes a subquery (you cannot put a window function in `WHERE`). DuckDB's `QUALIFY` filters on window results directly, like `HAVING` filters aggregates.

```python run
print(q("""
SELECT user_id, order_id, order_time, plan
FROM orders
QUALIFY row_number() OVER (PARTITION BY user_id ORDER BY order_time, order_id) = 1
ORDER BY order_time
LIMIT 4
""").to_string(index=False))
```
```text
 user_id  order_id                    order_time    plan
    1939      9001 2025-01-03 13:07:46.553656487  annual
    2865      9002 2025-01-03 17:21:01.053190251 monthly
    3805      9003 2025-01-04 02:40:10.419495099  annual
     229      9004 2025-01-04 22:49:52.242142530 monthly
```

The portable form, which runs on every database, wraps the same idea in a subquery:

```python run
portable = q("""
SELECT user_id, order_id, order_time, plan
FROM (SELECT *, row_number() OVER (PARTITION BY user_id ORDER BY order_time, order_id) AS rn FROM orders)
WHERE rn = 1
""")
qualify = q("""
SELECT user_id, order_id, order_time, plan FROM orders
QUALIFY row_number() OVER (PARTITION BY user_id ORDER BY order_time, order_id) = 1
""")
print("rows:", len(portable), "| same result:", portable.sort_values("user_id").reset_index(drop=True).equals(qualify.sort_values("user_id").reset_index(drop=True)))
print("users who bought at least once:", orders["user_id"].nunique())
```
```text
rows: 661 | same result: True
users who bought at least once: 661
```

One row per buyer: 661 first orders for 697 orders. The `row_number() = 1` pattern is also the standard way to **de-duplicate**: keep one row per key and say, in the `ORDER BY`, which one wins (you wrote the same rule, "newest wins", in da.05).

And a top-N with ties handled on purpose: the three most expensive months per country need `dense_rank` if ties must all stay, or `row_number` if exactly three rows are required.

```python run
print(q("""
WITH m AS (
  SELECT u.country, date_trunc('month', o.order_time)::DATE AS month, SUM(o.amount) AS revenue
  FROM orders o JOIN users u USING (user_id)
  GROUP BY 1, 2
)
SELECT country, month, revenue, rank() OVER (PARTITION BY country ORDER BY revenue DESC) AS revenue_rank
FROM m
QUALIFY revenue_rank <= 2
ORDER BY country, revenue_rank
""").to_string(index=False))
```
```text
country      month    revenue  revenue_rank
     IN 2025-05-01 131,925.00             1
     IN 2025-03-01 119,921.00             2
     UK 2025-05-01  37,973.00             1
     UK 2025-03-01  24,985.00             2
     US 2025-03-01  63,464.00             1
     US 2025-05-01  53,969.00             2
```

The join `orders` to `users` is many-to-one (`users.user_id` is unique), so it cannot multiply rows: the relationship check of da.06 passes. A window rank inside `QUALIFY` can use the alias it just created.

### 4.8 Gaps and islands: streaks

A classic analytic puzzle: find runs of consecutive days. The trick: for sorted days, `day - row_number()` is **constant inside a run** and jumps when a day is missed. Group by that constant and every group is one run (an "island").

```python run
print(q("""
WITH d AS (                                    -- grain: one row per user and login day
  SELECT DISTINCT user_id, event_time::DATE AS day FROM events WHERE event_type = 'login'
),
n AS (
  SELECT user_id, day, day - CAST(row_number() OVER (PARTITION BY user_id ORDER BY day) AS INTEGER) AS island
  FROM d
),
streaks AS (                                   -- grain: one row per streak
  SELECT user_id, MIN(day) AS first_day, MAX(day) AS last_day, COUNT(*) AS days_in_row
  FROM n GROUP BY user_id, island
)
SELECT * FROM streaks ORDER BY days_in_row DESC, user_id LIMIT 4
""").to_string(index=False))
```
```text
 user_id  first_day   last_day  days_in_row
    3288 2025-03-22 2025-04-02           12
    2507 2025-05-20 2025-05-28            9
    3528 2025-03-07 2025-03-15            9
    3920 2025-04-24 2025-05-02            9
```

Check one streak by hand: the number of days between `first_day` and `last_day` plus one should equal `days_in_row`.

```python run
chk = q("""
WITH d AS (SELECT DISTINCT user_id, event_time::DATE AS day FROM events WHERE event_type = 'login'),
n AS (SELECT user_id, day, day - CAST(row_number() OVER (PARTITION BY user_id ORDER BY day) AS INTEGER) AS island FROM d),
streaks AS (SELECT user_id, MIN(day) AS first_day, MAX(day) AS last_day, COUNT(*) AS days_in_row FROM n GROUP BY user_id, island)
SELECT COUNT(*) AS streaks, SUM(CASE WHEN date_diff('day', first_day, last_day) + 1 = days_in_row THEN 0 ELSE 1 END) AS broken_streaks,
       MAX(days_in_row) AS longest
FROM streaks
""")
print(chk.to_string(index=False))
```
```text
 streaks  broken_streaks  longest
   39483            0.00       12
```

`broken_streaks` is 0: every streak is gap-free. Without `DISTINCT` in the first CTE, two logins on one day would give the same day twice, and the trick would break: the trap is a duplicate row, which is why we de-duplicate to the grain "user and day" before numbering.

### 4.9 Sessions from events

A **session** is a burst of activity: events with no pause longer than some limit (30 or 60 minutes). SQL has no session function, but two windows build it: `lag` marks the start of a new session, and a running `SUM` of those marks numbers the sessions.

```python run
sessions = q("""
WITH e AS (
  SELECT user_id, event_time, event_type,
         lag(event_time) OVER (PARTITION BY user_id ORDER BY event_time) AS prev_time
  FROM events WHERE event_type <> 'login'
),
flagged AS (
  SELECT *, CASE WHEN prev_time IS NULL OR event_time - prev_time > INTERVAL 60 MINUTE THEN 1 ELSE 0 END AS new_session
  FROM e
),
numbered AS (
  SELECT *, SUM(new_session) OVER (PARTITION BY user_id ORDER BY event_time ROWS UNBOUNDED PRECEDING) AS session_no
  FROM flagged
)
SELECT user_id, session_no, MIN(event_time) AS started, COUNT(*) AS events, date_diff('minute', MIN(event_time), MAX(event_time)) AS minutes
FROM numbered GROUP BY user_id, session_no
""")
print(len(sessions), "sessions;", sessions["user_id"].nunique(), "users")
print(sessions["events"].describe().round(2).to_string())
print(sessions.sort_values(["events", "user_id"], ascending=False).head(3).to_string(index=False))
```
```text
5507 sessions; 3465 users
count   5,507.00
mean        2.02
std         1.13
min         1.00
25%         1.00
50%         2.00
75%         3.00
max         7.00
 user_id  session_no             started  events  minutes
    3959        1.00 2025-06-17 17:05:00       7      117
    2342        1.00 2025-03-26 15:52:00       7      114
    1531        1.00 2025-03-13 01:11:00       7      149
```

Three steps: **flag** where a session starts, **number** the sessions with a running sum of the flags, **group** by user and session number. This "flag, cumulative sum, group" recipe works for any "split a sequence into runs" problem. The limit of 60 minutes is a *definition*: write it in the metric document. A different limit gives a different number of sessions.

## 5. Calendars and dates

### 5.1 The problem of missing days

A table of events has rows only for days that **had** events. A day with zero orders is simply absent, so a plain `GROUP BY day` cannot show a zero, and moving averages count the wrong number of days. The cure is a **calendar** (also called a date spine): a table with one row for every day, to which you `LEFT JOIN` the facts.

```python run
print(q("""
SELECT * FROM generate_series(DATE '2025-07-10', DATE '2025-07-15', INTERVAL 1 DAY) AS t(day)
""").to_string(index=False))
```
```text
       day
2025-07-10
2025-07-11
2025-07-12
2025-07-13
2025-07-14
2025-07-15
```

`generate_series(start, end, step)` builds the calendar inside the query, with no extra table. (PostgreSQL has the same function; SQLite needs a recursive CTE.)

```python run
print(q("""
WITH cal AS (                                          -- grain: one row per calendar day
  SELECT CAST(d AS DATE) AS day FROM generate_series(DATE '2025-01-01', DATE '2025-07-15', INTERVAL 1 DAY) AS t(d)
),
rev AS (                                               -- grain: one row per day with orders
  SELECT order_time::DATE AS day, SUM(amount) AS revenue FROM orders GROUP BY 1
)
SELECT COUNT(*) AS calendar_days,
       COUNT(r.day) AS days_with_orders,
       COUNT(*) - COUNT(r.day) AS days_without_orders
FROM cal LEFT JOIN rev r USING (day)
"""
).to_string(index=False))
```
```text
 calendar_days  days_with_orders  days_without_orders
           196               185                   11
```

All 196 days of the calendar exist; only some have orders. For a moving average that treats an empty day as zero, join, `COALESCE` the revenue to 0, then average over the rows (now one row = one day, so `ROWS` and `RANGE` agree):

```python run
print(q("""
WITH cal AS (SELECT CAST(d AS DATE) AS day FROM generate_series(DATE '2025-01-01', DATE '2025-07-15', INTERVAL 1 DAY) AS t(d)),
rev AS (SELECT order_time::DATE AS day, SUM(amount) AS revenue FROM orders GROUP BY 1),
filled AS (SELECT c.day, COALESCE(r.revenue, 0) AS revenue FROM cal c LEFT JOIN rev r USING (day))
SELECT day, revenue,
       ROUND(AVG(revenue) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 0) AS avg_7_days
FROM filled ORDER BY day LIMIT 5 OFFSET 100
""").to_string(index=False))
```
```text
       day  revenue  avg_7_days
2025-04-11   499.00    7,352.00
2025-04-12 8,497.00    7,639.00
2025-04-13 6,494.00    7,852.00
2025-04-14 5,995.00    7,852.00
2025-04-15   499.00    7,567.00
```

The first 6 days of the series have a window with fewer than 7 days; many teams show `NULL` there, with `CASE WHEN row_number() OVER (ORDER BY day) >= 7 THEN ... END`. Say which you chose.

**Which is right, zero or absent?** For revenue, a day without orders is a true zero. For a metric such as "average order value", an empty day is *not* zero but undefined: averaging zeros in would drag the value down. As in da.05: ask what the missing row means.

### 5.2 Active users per day, week and month: DAU, WAU, MAU

"Active user" needs a definition: here, **a user with a `login` event in the period**. Because users repeat, the counts are distinct counts, and (da.06) distinct counts are not additive: the 7 daily counts of a week do not add up to the weekly count.

```python run
print(q("""
WITH l AS (SELECT DISTINCT user_id, event_time::DATE AS day FROM events WHERE event_type = 'login'),   -- grain: user and day
dau AS (SELECT day, COUNT(*) AS users FROM l GROUP BY day),
week AS (SELECT date_trunc('week', day)::DATE AS week, COUNT(DISTINCT user_id) AS wau FROM l GROUP BY 1)
SELECT w.week, w.wau,
       (SELECT SUM(users) FROM dau WHERE date_trunc('week', day)::DATE = w.week) AS sum_of_daily_counts,
       ROUND((SELECT AVG(users) FROM dau WHERE date_trunc('week', day)::DATE = w.week), 0) AS avg_dau
FROM week w ORDER BY w.week DESC LIMIT 5
""").to_string(index=False))
```
```text
      week  wau  sum_of_daily_counts  avg_dau
2025-07-14  329               329.00   329.00
2025-07-07 1133             2,366.00   338.00
2025-06-30 1205             2,594.00   371.00
2025-06-23 1322             2,813.00   402.00
2025-06-16 1337             2,835.00   405.00
```

The sum of the daily counts is about twice the weekly distinct count (2,366 against 1,133 in the week of 7 July); the weekly figure is the true number of different users. A "DAU divided by MAU" ratio, called **stickiness**, therefore uses the *average* DAU over the month and the distinct MAU. Compute it for complete months only (July is partial):

```python run
print(q("""
WITH l AS (SELECT DISTINCT user_id, event_time::DATE AS day FROM events WHERE event_type = 'login'),
dau AS (SELECT day, COUNT(*) AS users FROM l GROUP BY day),
m AS (SELECT date_trunc('month', day)::DATE AS month, COUNT(DISTINCT user_id) AS mau FROM l GROUP BY 1),
a AS (SELECT date_trunc('month', day)::DATE AS month, AVG(users) AS avg_dau FROM dau GROUP BY 1)
SELECT month, mau, ROUND(avg_dau, 1) AS avg_dau, ROUND(avg_dau * 100.0 / mau, 1) AS stickiness_pct
FROM m JOIN a USING (month) WHERE month < DATE '2025-07-01' ORDER BY month
""").to_string(index=False))
```
```text
     month  mau  avg_dau  stickiness_pct
2025-01-01  644    96.90           15.10
2025-02-01 1127   207.00           18.40
2025-03-01 1564   283.80           18.10
2025-04-01 1828   338.50           18.50
2025-05-01 2167   376.20           17.40
2025-06-01 2291   399.60           17.40
```

Stickiness is stable at 17 to 18 percent from February on. January is lower (15 percent) for a simple reason: its users signed up during the month, so on average they had only part of the month to be active. The ratio depends on how long users had to log in: a **period-length effect** to remember when a growing base is compared with an old one. The cohort view (section 6) removes this by following each group from its own start.

### 5.3 Period over period

Growth needs the previous period next to the current one: `lag` over the ordered periods. If a period is missing in the table, `lag` jumps to an older period (da.04 warned you about `shift` and missing months): build the periods from a calendar first.

```python run
print(q("""
WITH w AS (
  SELECT date_trunc('week', signup_at)::DATE AS week, COUNT(*) AS signups
  FROM users GROUP BY 1
)
SELECT week, signups,
       lag(signups) OVER (ORDER BY week) AS prev_week,
       ROUND((signups - lag(signups) OVER (ORDER BY week)) * 100.0 / NULLIF(lag(signups) OVER (ORDER BY week), 0), 1) AS growth_pct
FROM w ORDER BY week LIMIT 6
""").to_string(index=False))
```
```text
      week  signups  prev_week  growth_pct
2024-12-30      103       <NA>         NaN
2025-01-06      156        103       51.50
2025-01-13      145        156       -7.10
2025-01-20      131        145       -9.70
2025-01-27      152        131       16.00
2025-02-03      144        152       -5.30
```

The first week of 2025 is a partial week (1 January 2025 was a Wednesday), so its count is smaller and the first growth number is inflated. **Partial periods at the edges** are a standing trap: the first and the last periods are often incomplete. Either drop them or label them (da.06, section 8.5).

> **Try it.** Use `lead` instead of `lag` to find, for each user's login, the number of days until the *next* login, and compute the share of users' last logins that are older than 30 days before the extraction (users who may have churned). What does a `NULL` from `lead` mean?

<details><summary>Answer</summary>

```python run
print(q("""
WITH l AS (
  SELECT user_id, event_time::DATE AS day,
         lead(event_time::DATE) OVER (PARTITION BY user_id ORDER BY event_time) AS next_day
  FROM events WHERE event_type = 'login'
),
last_login AS (SELECT user_id, MAX(day) AS last_day FROM l GROUP BY user_id)
SELECT COUNT(*) AS users,
       COUNT(*) FILTER (WHERE date_diff('day', last_day, DATE '2025-07-15') > 30) AS silent_over_30_days,
       ROUND(COUNT(*) FILTER (WHERE date_diff('day', last_day, DATE '2025-07-15') > 30) * 100.0 / COUNT(*), 1) AS pct_silent
FROM last_login
""").to_string(index=False))
print(q("SELECT COUNT(*) AS logins_without_a_next_login FROM (SELECT lead(event_time) OVER (PARTITION BY user_id ORDER BY event_time) AS nxt FROM events WHERE event_type = 'login') WHERE nxt IS NULL").to_string(index=False))
```
```text
 users  silent_over_30_days  pct_silent
  4000                 1895       47.40
 logins_without_a_next_login
                        4000
```

A `NULL` from `lead` means "there is no later login": it is the user's last one, so there is exactly one per user, and the second query returns 4,000 (every user has at least the signup login). It does not mean the user churned: they may log in tomorrow. The first query finds 1,895 users (47.4 percent) whose last login is more than 30 days old. "Silent for more than 30 days" is a **definition of churn** that you must state, and it applies fairly only to users whose observation window is long enough: a user who signed up two weeks ago cannot be silent for 30 days. That point returns in section 6.

</details>


## 6. Cohort retention

### 6.1 The question

A growing app shows a rising number of active users. That number hides the question the business cares about: **do the people who join stay?** Total activity mixes old users and new ones, so it cannot answer. A **cohort** is a group of users who share a starting moment (here: the month of sign-up). **Retention** follows each cohort over time and asks, for each period after the start: what share of the cohort is still active?

To build the table without ambiguity, write the definition first (da.06):

| Ingredient | Definition for this chapter |
|---|---|
| Grain of the result | one row per cohort and per month since sign-up |
| Cohort | the calendar month of `signup_at` |
| Active | the user has at least one `login` event in the calendar month |
| Month index `k` | `0` for the sign-up month, `1` for the next calendar month, and so on |
| Numerator | **distinct** users of the cohort active in month `k` |
| Denominator | the **cohort size**: the distinct users who signed up in that month |
| Complete months only | activity before 1 July 2025; July is partial (the data end on 15 July) |
| Maturity | a cohort has a cell for `k` only if month `cohort + k` is a complete month |

The last two lines are the ones that analysts forget, and they are what the outcome of this chapter is about.

### 6.2 Build it in steps

Three small CTEs, each with one grain.

```python run
print(q("""
WITH cohort AS (                  -- grain: one row per user
  SELECT user_id, date_trunc('month', signup_at)::DATE AS cohort_month FROM users
),
activity AS (                     -- grain: one row per user and calendar month with at least one login
  SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS activity_month
  FROM events
  WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01'
)
SELECT c.cohort_month, a.activity_month,
       date_diff('month', c.cohort_month, a.activity_month) AS k
FROM cohort c JOIN activity a USING (user_id)
WHERE c.user_id IN (1939, 2804)
ORDER BY c.user_id, a.activity_month
"""
).to_string(index=False))
```
```text
cohort_month activity_month  k
  2025-01-01     2025-01-01  0
  2025-01-01     2025-03-01  2
  2025-01-01     2025-01-01  0
  2025-01-01     2025-06-01  5
```

Each row says: this user (in this cohort) was active in this month, `k` months after the start. Both users signed up on 1 January, and the rows list the months in which they logged in at least once. Notice that `activity` uses `DISTINCT`: without it, a user with 15 logins in a month would appear 15 times and be counted 15 times. **De-duplicate to the grain of the question** (user and month) before counting.

Now aggregate: for each cohort and `k`, the number of distinct active users; and the cohort size.

```python run
retention = q("""
WITH cohort AS (
  SELECT user_id, date_trunc('month', signup_at)::DATE AS cohort_month FROM users
),
size AS (                         -- grain: one row per cohort
  SELECT cohort_month, COUNT(*) AS cohort_size FROM cohort GROUP BY 1
),
activity AS (                     -- grain: one row per user and active month
  SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS activity_month
  FROM events WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01'
),
counts AS (                       -- grain: one row per cohort and month index
  SELECT c.cohort_month, date_diff('month', c.cohort_month, a.activity_month) AS k, COUNT(DISTINCT c.user_id) AS active_users
  FROM cohort c JOIN activity a USING (user_id)
  GROUP BY 1, 2
)
SELECT cohort_month, k, active_users, cohort_size, ROUND(active_users * 100.0 / cohort_size, 1) AS retention_pct
FROM counts JOIN size USING (cohort_month)
ORDER BY cohort_month, k
""")
print(retention.head(8).to_string(index=False))
print("rows:", len(retention))
```
```text
cohort_month  k  active_users  cohort_size  retention_pct
  2025-01-01  0           644          644         100.00
  2025-01-01  1           509          644          79.00
  2025-01-01  2           370          644          57.50
  2025-01-01  3           262          644          40.70
  2025-01-01  4           251          644          39.00
  2025-01-01  5           208          644          32.30
  2025-02-01  0           618          618         100.00
  2025-02-01  1           464          618          75.10
rows: 21
```

This is the **long** form: one row per cohort and `k`, the form to store and to chart. Rows for `k = 0` show 100 percent by construction, because the sign-up counts as a login. Many teams define month 0 this way and read the curve from month 1; say so in the report.

### 6.3 The matrix

The familiar triangle puts cohorts in rows and `k` in columns. In SQL, you can turn the long form into a matrix with conditional aggregation (portable) or with DuckDB's `PIVOT`.

```python run
view = retention.pivot(index="cohort_month", columns="k", values="retention_pct")
view.columns = [f"M{c}" for c in view.columns]
view.insert(0, "size", retention.groupby("cohort_month")["cohort_size"].first())
print(view.to_string())
```
```text
              size     M0    M1    M2    M3    M4    M5
cohort_month                                           
2025-01-01     644 100.00 79.00 57.50 40.70 39.00 32.30
2025-02-01     618 100.00 75.10 55.20 44.80 36.60   NaN
2025-03-01     730 100.00 74.10 55.20 44.50   NaN   NaN
2025-04-01     684 100.00 77.00 51.90   NaN   NaN   NaN
2025-05-01     709 100.00 79.30   NaN   NaN   NaN   NaN
2025-06-01     615 100.00   NaN   NaN   NaN   NaN   NaN
```

The shape is a **triangle**: January, the oldest cohort, has six months of history; June has one. The cells that would lie below the diagonal are empty (shown as `NaN`) because those months are not yet complete. That emptiness is *information* ("not yet observed"), and it must stay empty. What goes wrong when it does not?

In SQL, the same matrix with conditional aggregation:

```python run
print(q("""
WITH r AS (
  SELECT c.cohort_month, date_diff('month', c.cohort_month, a.activity_month) AS k, COUNT(DISTINCT c.user_id) AS active_users
  FROM (SELECT user_id, date_trunc('month', signup_at)::DATE AS cohort_month FROM users) c
  JOIN (SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS activity_month FROM events
        WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01') a USING (user_id)
  GROUP BY 1, 2),
s AS (SELECT date_trunc('month', signup_at)::DATE AS cohort_month, COUNT(*) AS n FROM users GROUP BY 1)
SELECT cohort_month, n AS size,
       ROUND(MAX(active_users) FILTER (WHERE k = 1) * 100.0 / n, 1) AS M1,
       ROUND(MAX(active_users) FILTER (WHERE k = 2) * 100.0 / n, 1) AS M2,
       ROUND(MAX(active_users) FILTER (WHERE k = 3) * 100.0 / n, 1) AS M3
FROM r JOIN s USING (cohort_month) GROUP BY cohort_month, n ORDER BY cohort_month
""").to_string(index=False))
```
```text
cohort_month  size    M1    M2    M3
  2025-01-01   644 79.00 57.50 40.70
  2025-02-01   618 75.10 55.20 44.80
  2025-03-01   730 74.10 55.20 44.50
  2025-04-01   684 77.00 51.90   NaN
  2025-05-01   709 79.30   NaN   NaN
  2025-06-01   615   NaN   NaN   NaN
```

`MAX(...) FILTER (WHERE k = 1)` picks the one value for that `k` (there is one row per cohort and `k`, so `MAX` is only a way to take it). For a cohort with no row for `k` the result is `NULL`: "not observed" or "nobody active", and these two are not the same, which brings us to the main danger of this chapter.

### 6.4 The immature cell: `NULL` is not zero

Suppose the query is written the other way: with a `LEFT JOIN` from a full grid of (cohort, k) combinations, or with `COALESCE(active_users, 0)`. Then the June cohort at `k = 3` would show **0 percent**. The reader would conclude "June users all vanished after three months", although three months have simply not passed.

We make the difference visible. First, a grid with every cohort and every `k` from 0 to 5, with the naive zeros:

```python run
naive = q("""
WITH cohort AS (SELECT user_id, date_trunc('month', signup_at)::DATE AS cohort_month FROM users),
size AS (SELECT cohort_month, COUNT(*) AS n FROM cohort GROUP BY 1),
grid AS (SELECT cohort_month, n, k FROM size CROSS JOIN generate_series(0, 5) AS g(k)),
act AS (
  SELECT c.cohort_month, date_diff('month', c.cohort_month, a.m) AS k, COUNT(DISTINCT c.user_id) AS active_users
  FROM cohort c JOIN (SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS m FROM events
                      WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01') a USING (user_id)
  GROUP BY 1, 2)
SELECT g.cohort_month, g.k, COALESCE(a.active_users, 0) * 100.0 / g.n AS naive_pct
FROM grid g LEFT JOIN act a ON a.cohort_month = g.cohort_month AND a.k = g.k
ORDER BY 1, 2
""")
print(naive.pivot(index="cohort_month", columns="k", values="naive_pct").round(1).to_string())
```
```text
k                 0     1     2     3     4     5
cohort_month                                     
2025-01-01   100.00 79.00 57.50 40.70 39.00 32.30
2025-02-01   100.00 75.10 55.20 44.80 36.60  0.00
2025-03-01   100.00 74.10 55.20 44.50  0.00  0.00
2025-04-01   100.00 77.00 51.90  0.00  0.00  0.00
2025-05-01   100.00 79.30  0.00  0.00  0.00  0.00
2025-06-01   100.00  0.00  0.00  0.00  0.00  0.00
```

The lower-right corner is full of zeros: the cells for months that have not happened. A chart of this matrix shows a cliff along the diagonal, and someone will ask what went wrong in May. The fix is a rule, written in SQL: a cell exists only if its month is complete.

```python run
fixed = q("""
WITH cohort AS (SELECT user_id, date_trunc('month', signup_at)::DATE AS cohort_month FROM users),
size AS (SELECT cohort_month, COUNT(*) AS n FROM cohort GROUP BY 1),
grid AS (
  SELECT cohort_month, n, k FROM size CROSS JOIN generate_series(0, 5) AS g(k)
  WHERE cohort_month + to_months(k) < DATE '2025-07-01'              -- the month cohort+k must be complete (before July)
),
act AS (
  SELECT c.cohort_month, date_diff('month', c.cohort_month, a.m) AS k, COUNT(DISTINCT c.user_id) AS active_users
  FROM cohort c JOIN (SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS m FROM events
                      WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01') a USING (user_id)
  GROUP BY 1, 2)
SELECT g.cohort_month, g.k, COALESCE(a.active_users, 0) * 100.0 / g.n AS retention_pct
FROM grid g LEFT JOIN act a ON a.cohort_month = g.cohort_month AND a.k = g.k
ORDER BY 1, 2
""")
fx = fixed.pivot(index="cohort_month", columns="k", values="retention_pct").round(1)
print(fx.to_string())
print()
print("same cells as the first matrix (where both exist):", bool(np.allclose(fx.to_numpy(float)[~np.isnan(fx.to_numpy(float))], view.drop(columns="size").to_numpy(float)[~np.isnan(fx.to_numpy(float))], atol=0.06)))
```
```text
k                 0     1     2     3     4     5
cohort_month                                     
2025-01-01   100.00 79.00 57.50 40.70 39.00 32.30
2025-02-01   100.00 75.10 55.20 44.80 36.60   NaN
2025-03-01   100.00 74.10 55.20 44.50   NaN   NaN
2025-04-01   100.00 77.00 51.90   NaN   NaN   NaN
2025-05-01   100.00 79.30   NaN   NaN   NaN   NaN
2025-06-01   100.00   NaN   NaN   NaN   NaN   NaN

same cells as the first matrix (where both exist): True
```

Now the `LEFT JOIN` is used correctly: the grid decides which cells **exist** (complete months only), and `COALESCE(..., 0)` turns a missing count into zero *only inside that grid*, where zero is a real observation ("nobody was active"). Outside the grid, there is no row, so there is no number. The rule in one sentence: **zero means "observed and nobody"; missing means "not observed yet".**

> **Predict the output.** If the July column were included without any care (that is, if the filter `event_time < '2025-07-01'` were removed), what would the retention of the January cohort be in July (k = 6), compared with June (k = 5)? What would it look like on a chart?

<details><summary>Answer</summary>

```python run
partial = q("""
WITH c AS (SELECT user_id, date_trunc('month', signup_at)::DATE AS cohort_month FROM users WHERE signup_at < TIMESTAMP '2025-02-01'),
a AS (SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS m FROM events WHERE event_type = 'login')
SELECT date_diff('month', c.cohort_month, a.m) AS k, COUNT(DISTINCT c.user_id) AS active, ROUND(COUNT(DISTINCT c.user_id) * 100.0 / (SELECT COUNT(*) FROM c), 1) AS pct
FROM c JOIN a USING (user_id) GROUP BY 1 ORDER BY 1
""")
print(partial.to_string(index=False))
```
```text
 k  active    pct
 0     644 100.00
 1     509  79.00
 2     370  57.50
 3     262  40.70
 4     251  39.00
 5     208  32.30
 6     118  18.30
```

The July value (k = 6) is lower than June (k = 5), a sharp fall at the end of an otherwise smooth curve. The cause is not that users left: July holds only 15 days of data, so a user who logs in about once a month has a good chance not to have logged in *yet*. The chart shows a fake cliff on the last point. Both rules, "complete months only" and "no cell for months that have not happened", exist to prevent this one picture.

</details>

### 6.5 The pooled retention curve

How should we summarise all cohorts in one curve ("the typical retention after `k` months")? The tempting method is the simple mean of the percentages in a column. By da.06 that is an **average of averages**. The correct pooled curve adds the numerators and the denominators over the cohorts that have reached `k`, then divides once.

```python run
pool = q("""
WITH cohort AS (SELECT user_id, date_trunc('month', signup_at)::DATE AS cohort_month FROM users),
act AS (
  SELECT c.cohort_month, date_diff('month', c.cohort_month, a.m) AS k, COUNT(DISTINCT c.user_id) AS active_users
  FROM cohort c JOIN (SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS m FROM events
                      WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01') a USING (user_id)
  GROUP BY 1, 2),
size AS (SELECT cohort_month, COUNT(*) AS n FROM cohort GROUP BY 1)
SELECT a.k,
       COUNT(*)                                              AS cohorts_observed,
       ROUND(AVG(a.active_users * 100.0 / s.n), 2)           AS simple_average_of_pcts,
       ROUND(SUM(a.active_users) * 100.0 / SUM(s.n), 2)      AS pooled_pct
FROM act a JOIN size s USING (cohort_month)
GROUP BY a.k ORDER BY a.k
""")
print(pool.to_string(index=False))
```
```text
 k  cohorts_observed  simple_average_of_pcts  pooled_pct
 0                 6                  100.00      100.00
 1                 5                   76.91       76.90
 2                 4                   54.93       54.90
 3                 3                   43.34       43.37
 4                 2                   37.77       37.80
 5                 1                   32.30       32.30
```

Each row says how many cohorts have reached month `k`, so the oldest cohorts supply the far points: the value at `k = 5` rests on a single cohort (January). The pooled and the simple averages differ in the second decimal, because the cohorts are similar in size here; with cohorts of 100 and 5,000 users they would differ a lot. And a curve whose last points rest on one cohort should show that: **report the number of cohorts behind every point.**

### 6.6 Day-N retention

Product teams also use **day-N retention**, measured in days from each user's own sign-up moment instead of calendar months. "D30 retention" asks: of the users who signed up, what share came back 30 days later? Three definitions exist, and they give three different numbers.

| Name | Active if... |
|---|---|
| Exact day (classic) | the user logged in **on** day 30 after sign-up |
| Within a window | the user logged in on any of days 1 to 30 |
| On or after (unbounded) | the user logged in on day 30 **or any later day** |

```python run
d30 = q("""
WITH u AS (SELECT user_id, signup_at::DATE AS d0 FROM users WHERE signup_at::DATE + 30 <= DATE '2025-07-15'),   -- eligible: 30 days observed
l AS (SELECT DISTINCT user_id, event_time::DATE AS d FROM events WHERE event_type = 'login'),
j AS (SELECT u.user_id, date_diff('day', u.d0, l.d) AS day_n FROM u LEFT JOIN l ON l.user_id = u.user_id)
SELECT COUNT(DISTINCT user_id) AS eligible_users,
       ROUND(COUNT(DISTINCT user_id) FILTER (WHERE day_n = 30) * 100.0 / COUNT(DISTINCT user_id), 1) AS exact_day_30,
       ROUND(COUNT(DISTINCT user_id) FILTER (WHERE day_n BETWEEN 1 AND 30) * 100.0 / COUNT(DISTINCT user_id), 1) AS within_30_days,
       ROUND(COUNT(DISTINCT user_id) FILTER (WHERE day_n >= 30) * 100.0 / COUNT(DISTINCT user_id), 1) AS day_30_or_after
FROM j
""")
print(d30.to_string(index=False))
```
```text
 eligible_users  exact_day_30  within_30_days  day_30_or_after
           3714         17.10           94.10            75.20
```

Three numbers for "D30 retention", and the order is always `exact day <= within 30 days` and `exact day <= on or after`. The exact-day version is the strictest and the noisiest (it depends on one single day, perhaps a Sunday); the "within" version is the most generous, since almost every user logs in at least once in a month; the unbounded version is the closest to "has the user not churned". None is wrong. **Name the version.**

Note the first line of the query: **eligible users only**. A user who signed up on 10 July cannot have a "day 30" before 9 August, and the data end on 15 July. Counting such users in the denominator pushes retention down, for the same reason that immature cohorts did. Compare:

```python run
print(q("""
SELECT 'all users' AS denominator, COUNT(*) AS users,
       ROUND(COUNT(*) FILTER (WHERE EXISTS (SELECT 1 FROM events e WHERE e.user_id = u.user_id AND e.event_type = 'login'
                                            AND e.event_time::DATE = u.signup_at::DATE + 30)) * 100.0 / COUNT(*), 1) AS exact_day_30
FROM users u
UNION ALL
SELECT 'eligible users only', COUNT(*),
       ROUND(COUNT(*) FILTER (WHERE EXISTS (SELECT 1 FROM events e WHERE e.user_id = u.user_id AND e.event_type = 'login'
                                            AND e.event_time::DATE = u.signup_at::DATE + 30)) * 100.0 / COUNT(*), 1)
FROM users u WHERE signup_at::DATE + 30 <= DATE '2025-07-15'
"""
).to_string(index=False))
```
```text
        denominator  users  exact_day_30
          all users   4000         15.90
eligible users only   3714         17.10
```

The naive denominator is lower because it includes the users who signed up between 16 and 30 June, whose day 30 lies in the future. The difference is modest here, because they are a small part of the 4,000 users, but when the cohort being measured is the *latest* one, which is the one a manager looks at first, the error is the whole story.

### 6.7 Retention by segment

Retention tables become decisions when you split them by a segment. Does the acquisition channel matter? Use the month-1 retention, for cohorts that have a complete month 1 (January to May).

```python run
print(q("""
WITH cohort AS (
  SELECT user_id, channel, date_trunc('month', signup_at)::DATE AS cohort_month FROM users
  WHERE signup_at < TIMESTAMP '2025-06-01'                      -- cohorts with a complete month 1
),
active_m1 AS (
  SELECT DISTINCT e.user_id FROM events e JOIN cohort c USING (user_id)
  WHERE e.event_type = 'login' AND date_trunc('month', e.event_time)::DATE = c.cohort_month + INTERVAL 1 MONTH
)
SELECT c.channel, COUNT(*) AS users, COUNT(a.user_id) AS retained_m1,
       ROUND(COUNT(a.user_id) * 100.0 / COUNT(*), 1) AS m1_retention_pct
FROM cohort c LEFT JOIN active_m1 a USING (user_id)
GROUP BY c.channel ORDER BY m1_retention_pct DESC
""").to_string(index=False))
```
```text
 channel  users  retained_m1  m1_retention_pct
referral    507          460             90.70
 organic   1687         1380             81.80
     ads   1191          763             64.10
```

Referral users are back in month 1 in 91 percent of the cases, organic users in 82 percent, and users from ads in only 64 percent: a gap of 27 points between the best and the worst channel. That is the kind of difference that moves a marketing budget. Two checks before you believe it, both from da.06: the join `cohort` to `active_m1` uses a unique key on the right (`DISTINCT user_id`), so it cannot multiply rows; and the channel mix per cohort should be similar, otherwise a change in the mix would look like a change in quality (Simpson's paradox). With synthetic data the mix is constant by construction; with real data, check it.

> **Try it.** Compute the retention matrix **by channel for the January cohort only**, months 0 to 3. Which channel loses users fastest between month 0 and month 1?

<details><summary>Answer</summary>

```python run
res = q("""
WITH c AS (SELECT user_id, channel FROM users WHERE signup_at < TIMESTAMP '2025-02-01'),
n AS (SELECT channel, COUNT(*) AS size FROM c GROUP BY 1),
a AS (SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS m FROM events
      WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01')
SELECT c.channel, date_diff('month', DATE '2025-01-01', a.m) AS k, COUNT(DISTINCT c.user_id) AS active, n.size
FROM c JOIN a USING (user_id) JOIN n USING (channel)
WHERE date_diff('month', DATE '2025-01-01', a.m) <= 3
GROUP BY c.channel, k, n.size ORDER BY c.channel, k
""")
res["pct"] = (res["active"] * 100 / res["size"]).round(1)
print(res.pivot(index="channel", columns="k", values="pct").to_string())
```
```text
k             0     1     2     3
channel                          
ads      100.00 68.00 39.70 23.10
organic  100.00 84.30 63.90 48.50
referral 100.00 90.80 82.70 61.20
```

Ads lose the most in the first step: from 100 percent in month 0 to 68 percent in month 1, against 91 percent for referral; by month 3 ads are at 23 percent and referral at 61. Organic sits between them. The differences are made in the first months and then widen, so a retention analysis often ends in one sentence like this: "ads users decide in the first month, and most decide to leave".

</details>

## 7. Funnels

### 7.1 The question

A **funnel** follows users through an ordered list of steps and counts how many reach each one. Ours: `view_course` → `add_to_cart` → `checkout_start` → `purchase`. The funnel answers: where do we lose people?

The trap is the same as in da.06: *what is counted at each step?* Compare two ways of counting the first step.

```python run
print(q("""
SELECT event_type,
       COUNT(*)                 AS events,
       COUNT(DISTINCT user_id)  AS users
FROM events
WHERE event_type <> 'login'
GROUP BY 1
ORDER BY CASE event_type WHEN 'view_course' THEN 1 WHEN 'add_to_cart' THEN 2 WHEN 'checkout_start' THEN 3 ELSE 4 END
""").to_string(index=False))
```
```text
    event_type  events  users
   view_course    8302   3332
   add_to_cart    1312   1312
checkout_start     798    798
      purchase     697    661
```

Views are 8,302 *events* but only 3,332 *users*: each user may view several times. A funnel built on events gives a first step 2.5 times too big, and conversion rates 2.5 times too small. **A funnel counts users (or sessions), never events**, unless the step is explicitly "event count". The same holds for purchases: 697 purchase events, but 661 buyers, because of renewals.

### 7.2 One row per user: the first time of each step

The standard way to build a funnel is to compute, for each user, the **first time** they did each step (or `NULL` if never). That gives a table at the grain of one row per user, which is easy to count, compare and order.

```python run
con.execute("""
CREATE OR REPLACE VIEW funnel_users AS
SELECT u.user_id, u.channel, u.signup_at,
       MIN(e.event_time) FILTER (WHERE e.event_type = 'view_course')    AS t_view,
       MIN(e.event_time) FILTER (WHERE e.event_type = 'add_to_cart')    AS t_cart,
       MIN(e.event_time) FILTER (WHERE e.event_type = 'checkout_start') AS t_checkout,
       MIN(e.event_time) FILTER (WHERE e.event_type = 'purchase')       AS t_purchase
FROM users u LEFT JOIN events e USING (user_id)
GROUP BY u.user_id, u.channel, u.signup_at
""")
print(q("SELECT COUNT(*) AS rows_, COUNT(DISTINCT user_id) AS users FROM funnel_users").to_string(index=False))
print(q("SELECT * FROM funnel_users WHERE t_purchase IS NOT NULL ORDER BY user_id LIMIT 3").to_string(index=False))
```
```text
 rows_  users
  4000   4000
 user_id channel           signup_at              t_view                        t_cart                    t_checkout                    t_purchase
       2 organic 2025-03-01 04:22:00 2025-03-02 12:27:00 2025-03-02 15:09:10.307274478 2025-03-03 11:19:57.143544791 2025-03-03 11:28:37.603384067
       9 organic 2025-04-26 18:59:00                 NaT                           NaT                           NaT 2025-05-01 18:59:00.000000000
      20 organic 2025-03-28 16:37:00 2025-03-31 00:44:00 2025-03-31 00:47:09.698337724 2025-03-31 06:34:31.096756790 2025-03-31 08:13:48.619212672
```

One row per user (4,000 = 4,000): the grain is right. The `LEFT JOIN` keeps users with no funnel events; their times are all `NULL`. Always keep the left side whole in a funnel: a user who did nothing is a drop-off, not a missing row.

### 7.3 Unordered against ordered

Two ways to say "reached step 3". **Unordered**: has a checkout event at all. **Ordered**: has a checkout event *after* the cart event, which was after the view. The difference matters when the data contain shortcuts, bots, or tracking gaps. Ours contain 3 percent of users who buy through a direct link, with a purchase event and no view, cart or checkout.

```python run
print(q("""
SELECT COUNT(*)                                                         AS users,
       COUNT(t_view)                                                    AS viewed,
       COUNT(t_cart)                                                    AS carted_any_order,
       COUNT(t_cart)     FILTER (WHERE t_cart >= t_view)                AS carted_after_view,
       COUNT(t_checkout) FILTER (WHERE t_checkout >= t_cart AND t_cart >= t_view) AS checkout_ordered,
       COUNT(t_purchase)                                                AS purchased_any_order,
       COUNT(t_purchase) FILTER (WHERE t_purchase >= t_checkout AND t_checkout >= t_cart AND t_cart >= t_view) AS purchased_ordered
FROM funnel_users
""").to_string(index=False))
```
```text
 users  viewed  carted_any_order  carted_after_view  checkout_ordered  purchased_any_order  purchased_ordered
  4000    3332              1312               1312               798                  661                528
```

Careful with `NULL`: `t_cart >= t_view` is unknown when either is `NULL`, so users who skipped a step fail the `FILTER`, which is what we want in a strict funnel. The unordered purchase count is higher than the ordered one by the direct-link buyers (users with a purchase but no earlier step). Both numbers are valid; they define different funnels. A product team wants the strict one to judge the page flow, and finance wants every buyer.

The cleanest way to present the funnel is as a table with the step, the users, the conversion from the previous step, and the conversion from the top:

```python run
funnel = q("""
WITH s AS (
  SELECT 1 AS step, 'view_course'    AS name, COUNT(*) FILTER (WHERE t_view IS NOT NULL) AS users FROM funnel_users
  UNION ALL SELECT 2, 'add_to_cart',    COUNT(*) FILTER (WHERE t_cart >= t_view) FROM funnel_users
  UNION ALL SELECT 3, 'checkout_start', COUNT(*) FILTER (WHERE t_checkout >= t_cart AND t_cart >= t_view) FROM funnel_users
  UNION ALL SELECT 4, 'purchase',       COUNT(*) FILTER (WHERE t_purchase >= t_checkout AND t_checkout >= t_cart AND t_cart >= t_view) FROM funnel_users
)
SELECT step, name, users,
       ROUND(users * 100.0 / lag(users) OVER (ORDER BY step), 1) AS pct_of_previous,
       ROUND(users * 100.0 / first_value(users) OVER (ORDER BY step), 1) AS pct_of_top,
       lag(users) OVER (ORDER BY step) - users AS dropped
FROM s ORDER BY step
""")
print(funnel.to_string(index=False))
```
```text
 step           name  users  pct_of_previous  pct_of_top  dropped
    1    view_course   3332              NaN      100.00     <NA>
    2    add_to_cart   1312            39.40       39.40     2020
    3 checkout_start    798            60.80       23.90      514
    4       purchase    528            66.20       15.80      270
```

The window functions of section 4 do all the work: `lag` for the previous step, `first_value` for the top. Read the funnel from the "pct_of_previous" column: the biggest relative loss is between view and cart (most viewers never add to cart), and only about two thirds of the people who start checkout complete it. The "pct_of_top" column tells how many views it takes to make a sale. Each ratio has a number behind it; show both.

### 7.4 By segment

A funnel by channel shows where each channel leaks. Do it in one query with the same conditions, grouped by channel.

```python run
by_channel = q("""
SELECT channel,
       COUNT(*) FILTER (WHERE t_view IS NOT NULL)                                          AS viewed,
       COUNT(*) FILTER (WHERE t_cart >= t_view)                                            AS carted,
       COUNT(*) FILTER (WHERE t_checkout >= t_cart AND t_cart >= t_view)                   AS checkout,
       COUNT(*) FILTER (WHERE t_purchase >= t_checkout AND t_checkout >= t_cart AND t_cart >= t_view) AS purchased
FROM funnel_users GROUP BY channel
""").set_index("channel")
rates = pd.DataFrame({
    "view->cart %": by_channel["carted"] / by_channel["viewed"] * 100,
    "cart->checkout %": by_channel["checkout"] / by_channel["carted"] * 100,
    "checkout->buy %": by_channel["purchased"] / by_channel["checkout"] * 100,
    "view->buy %": by_channel["purchased"] / by_channel["viewed"] * 100,
}).round(1)
print(by_channel.to_string())
print()
print(rates.to_string())
print("\nall channels together, view->buy %:", round(by_channel["purchased"].sum() / by_channel["viewed"].sum() * 100, 1))
```
```text
          viewed  carted  checkout  purchased
channel                                      
referral     496     264       155         97
ads         1187     364       230        152
organic     1649     684       413        279

          view->cart %  cart->checkout %  checkout->buy %  view->buy %
channel                                                               
referral         53.20             58.70            62.60        19.60
ads              30.70             63.20            66.10        12.80
organic          41.50             60.40            67.60        16.90

all channels together, view->buy %: 15.8
```

The overall conversion is the **pooled** rate (total buyers over total viewers), not the mean of the three channel rates: da.06 again. Referral converts best at the first step because that is where the generator gave it an edge; the later steps are alike, so the lever is early in the funnel. Small numbers in the cells (e.g. 40 or so users at the checkout step for a channel) mean that the percentages move a lot with a few users, so show the counts.

### 7.5 Time between steps

How long do users take? Use the first-time columns and the median (the distribution is skewed: some wait for days).

```python run
print(q("""
SELECT ROUND(median(date_diff('minute', t_view, t_cart)) / 60.0, 1)      AS median_hours_view_to_cart,
       ROUND(median(date_diff('minute', t_cart, t_checkout)) / 60.0, 1)  AS median_hours_cart_to_checkout,
       ROUND(median(date_diff('minute', t_checkout, t_purchase)), 0)     AS median_minutes_checkout_to_buy,
       ROUND(quantile_cont(date_diff('minute', t_view, t_cart) / 60.0, 0.9), 1) AS p90_hours_view_to_cart
FROM funnel_users
WHERE t_purchase >= t_checkout AND t_checkout >= t_cart AND t_cart >= t_view
"""
).to_string(index=False))
```
```text
 median_hours_view_to_cart  median_hours_cart_to_checkout  median_minutes_checkout_to_buy  p90_hours_view_to_cart
                     14.00                           6.80                           19.00                   42.50
```

This restricts to users who completed the funnel in order, so it measures time *among converters*. Users who never converted have no time. This is a form of **survivorship**: a median of 14 hours from view to cart among converters does not mean that a typical *viewer* decides in 14 hours. Always say which group a summary describes.

### 7.6 A conversion window

"Of the users who signed up, how many bought **within 7 days**?" A windowed conversion needs the same eligibility rule as D7 retention: only users observed for the whole window.

```python run
print(q("""
SELECT channel,
       COUNT(*) AS eligible_users,
       COUNT(*) FILTER (WHERE t_purchase IS NOT NULL AND t_purchase < signup_at + INTERVAL 7 DAY) AS bought_within_7_days,
       ROUND(COUNT(*) FILTER (WHERE t_purchase IS NOT NULL AND t_purchase < signup_at + INTERVAL 7 DAY) * 100.0 / COUNT(*), 2) AS conv_7d_pct
FROM funnel_users
WHERE signup_at + INTERVAL 7 DAY <= TIMESTAMP '2025-07-15'           -- the 7-day window must be fully observed
GROUP BY channel ORDER BY conv_7d_pct DESC
"""
).to_string(index=False))
```
```text
 channel  eligible_users  bought_within_7_days  conv_7d_pct
referral             597                   104        17.42
 organic            1976                   303        15.33
     ads            1427                   169        11.84
```

This counts the **first** purchase only, since `t_purchase` is the first time. It would double-count if you joined the orders table at the user level, since a renewal buyer has two orders: the fan-out of da.06.

## 8. Who is active: new, retained, resurrected, churned

### 8.1 Four states

Monthly active users (MAU) is one number made of four kinds of users. Splitting it explains *why* it moves. Using the months in which each user was active:

| State in month `m` | Definition |
|---|---|
| **New** | active in `m`, and `m` is the first month they were ever active |
| **Retained** | active in `m` and also active in `m - 1` |
| **Resurrected** | active in `m`, not active in `m - 1`, but active before that |
| **Churned** | active in `m - 1`, not active in `m` |

Two identities must hold, and they are the check of the query: `MAU(m) = new + retained + resurrected`, and `MAU(m-1) = retained + churned` (the churned in month `m` are the users of `m - 1` who did not continue).

```python run
states = q("""
WITH am AS (                       -- grain: one row per user and complete active month
  SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS month
  FROM events WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01'
),
lagged AS (
  SELECT user_id, month,
         lag(month) OVER (PARTITION BY user_id ORDER BY month) AS prev_month,
         lead(month) OVER (PARTITION BY user_id ORDER BY month) AS next_month
  FROM am
),
labelled AS (
  SELECT month,
         CASE WHEN prev_month IS NULL THEN 'new'
              WHEN prev_month = month - INTERVAL 1 MONTH THEN 'retained'
              ELSE 'resurrected' END AS state,
         user_id, next_month
  FROM lagged
)
SELECT month,
       COUNT(*)                                       AS mau,
       COUNT(*) FILTER (WHERE state = 'new')          AS new,
       COUNT(*) FILTER (WHERE state = 'retained')     AS retained,
       COUNT(*) FILTER (WHERE state = 'resurrected')  AS resurrected
FROM labelled GROUP BY month ORDER BY month
""")
states["churned"] = (states["mau"].shift(1) - states["retained"]).astype("Int64")
print(states.to_string(index=False))
```
```text
     month  mau  new  retained  resurrected  churned
2025-01-01  644  644         0            0     <NA>
2025-02-01 1127  618       509            0      135
2025-03-01 1564  730       787           47      340
2025-04-01 1828  684      1039          105      525
2025-05-01 2167  709      1217          241      611
2025-06-01 2291  615      1347          329      820
```

Verify the identities on the numbers, in code:

```python run
ok1 = (states["mau"] == states["new"] + states["retained"] + states["resurrected"]).all()
ok2 = (states["mau"].shift(1)[1:] == (states["retained"] + states["churned"])[1:]).all()
print("MAU = new + retained + resurrected  :", bool(ok1))
print("MAU(m-1) = retained(m) + churned(m) :", bool(ok2))
```
```text
MAU = new + retained + resurrected  : True
MAU(m-1) = retained(m) + churned(m) : True
```

Both identities hold for every month. The table is a story: MAU grows because the number of **new** users is large every month; the **churned** count grows with the base; **resurrected** users are a small stream of returners. If MAU were flat, this decomposition would show whether acquisition and churn were both zero or just balanced. The first month has no `churned` (nothing before it).

The pattern uses `lag` over months **that exist for the user**: `prev_month = month - INTERVAL 1 MONTH` tests that the previous *active* month is exactly the previous *calendar* month. If it is further back, the user was away, so they are resurrected. This is the case where an off-by-one in month arithmetic would silently turn retained users into resurrected ones.


## 9. DuckDB with pandas and Parquet

### 9.1 Moving between pandas and SQL

DuckDB and pandas are not rivals; analysts use both in one notebook. A DataFrame can be queried with SQL, and a query result returns as a DataFrame. Choose by the task: **SQL for set operations, windows and anything that reads like a question about groups; pandas for reshaping, plotting and Python logic.**

```python run
recent = users[users["signup_at"] >= "2025-06-01"]                    # an ordinary DataFrame
print(duckdb.sql("SELECT channel, COUNT(*) AS n FROM recent GROUP BY channel ORDER BY n DESC").df())
```
```text
    channel    n
0   organic  289
1       ads  236
2  referral   90
```

The SQL text mentions `recent`, a Python variable, and DuckDB found it: this is the **replacement scan** of section 1. It is convenient in a notebook and fragile in a large program (a typo in a variable name becomes a confusing error), so in programs prefer `con.register("name", df)`. The result type decides how the answer comes back:

```python run
rel = con.sql("SELECT channel, COUNT(*) AS n FROM users GROUP BY channel ORDER BY channel")
print(type(rel).__name__)
print(rel.df().dtypes.astype(str).to_dict())
print(rel.fetchall())                    # a list of Python tuples
print(type(rel.arrow()).__name__)        # an Arrow table: zero-copy hand-over to other tools
print(rel.pl().shape)                    # a Polars DataFrame
```
```text
DuckDBPyRelation
{'channel': 'str', 'n': 'int64'}
[('ads', 1427), ('organic', 1976), ('referral', 597)]
RecordBatchReader
(3, 2)
```

`con.sql(...)` returns a lazy **relation**: the query has not run yet; it runs when you ask for a result (`.df()`, `.fetchall()`, `.arrow()`, `.pl()`) or print it. A relation keeps no result between calls (in DuckDB 2.0 there is no `fetchone()` on a relation, and every call runs the query again), so save the DataFrame if you need it twice. A relation can be refined with Python methods, or used again inside another SQL query by name.

```python run
big = con.sql("SELECT user_id, channel FROM users WHERE country = 'IN'")
print(big.filter("channel = 'ads'").aggregate("count(*) AS indian_ads_users").fetchall()[0][0])
print(con.sql("SELECT COUNT(*) FROM big WHERE channel = 'referral'").fetchall()[0][0])
```
```text
858
364
```

The same question in the two styles. For a one-line groupby, pandas is shorter; as soon as a window or a join is involved, SQL is clearer.

```python run
sql_res = q("SELECT channel, country, COUNT(*) AS n, ROUND(AVG(date_diff('day', signup_at, TIMESTAMP '2025-07-15')), 1) AS avg_age_days FROM users GROUP BY ALL ORDER BY ALL")
pd_res = (users.assign(age_days=(END - users["signup_at"]).dt.total_seconds() / 86400)
               .groupby(["channel", "country"], as_index=False)
               .agg(n=("user_id", "size"), avg_age_days=("age_days", "mean"))
               .round({"avg_age_days": 1}))
print(sql_res.head(3).to_string(index=False))
print("same counts:", (sql_res["n"].to_numpy() == pd_res["n"].to_numpy()).all())
print("max difference in average age (days):", round(float((sql_res["avg_age_days"] - pd_res["avg_age_days"]).abs().max()), 2))
```
```text
channel country   n  avg_age_days
    ads      IN 858        105.90
    ads      UK 227        102.20
    ads      US 342        107.10
same counts: True
max difference in average age (days): 0.6
```

The counts agree exactly. The averages differ by up to 0.6 of a day, because `date_diff('day', ...)` counts day *boundaries* (a whole number) while the pandas version uses fractional days: the same boundary-against-elapsed difference as in section 2.4. The two tools did what we asked; we asked slightly different things.

### 9.2 Parquet

You met Parquet in shared.02 and da.03: a **column-oriented, typed, compressed** file format. For analytics it matters for three reasons. It **keeps types** (a CSV forgets that a column is a date; da.05). It is **small**, because similar values sit together and compress well. And it is **fast** to query, because the reader fetches only the columns the query uses.

DuckDB writes and reads Parquet in SQL.

```python run
import tempfile, pathlib, os
_tmp = tempfile.TemporaryDirectory()
tmp = pathlib.Path(_tmp.name)

con.execute(f"COPY (SELECT * FROM events) TO '{tmp / 'events.parquet'}' (FORMAT parquet)")
con.execute(f"COPY (SELECT * FROM events) TO '{tmp / 'events.csv'}' (FORMAT csv, HEADER)")
for f in ["events.parquet", "events.csv"]:
    print(f"{f:16} {os.path.getsize(tmp / f) / 1024:8.0f} KiB")
print(q(f"DESCRIBE SELECT * FROM '{tmp / 'events.parquet'}'")[["column_name", "column_type"]].to_string(index=False))
```
```text
events.parquet        817 KiB
events.csv           2498 KiB
column_name  column_type
   event_id       BIGINT
    user_id       BIGINT
 event_time TIMESTAMP_NS
 event_type      VARCHAR
```

Parquet is about three times smaller than the CSV here (the exact sizes depend on the compression library), and it remembers `TIMESTAMP`, `BIGINT` and `VARCHAR`. You can query a file as if it were a table, by putting its path in the `FROM` clause. No import step:

```python run
print(q(f"""
SELECT event_type, COUNT(*) AS events, COUNT(DISTINCT user_id) AS users
FROM '{tmp / 'events.parquet'}'
GROUP BY 1 ORDER BY events DESC
""").to_string(index=False))
```
```text
    event_type  events  users
         login   56312   4000
   view_course    8302   3332
   add_to_cart    1312   1312
checkout_start     798    798
      purchase     697    661
```

### 9.3 Reading only what you need

A columnar file lets the engine skip what the query does not use. Check what DuckDB plans with `EXPLAIN`: it names the columns it will read from the file.

```python run
plan = q(f"EXPLAIN SELECT COUNT(DISTINCT user_id) FROM '{tmp / 'events.parquet'}' WHERE event_type = 'purchase'")
text = plan.iloc[0, 1]
lines = [l.strip(" │┌┐└┘─") for l in text.splitlines()]
print([l for l in lines if l.startswith(("Function", "Filters", "Projections: user_id"))])
```
```text
['Projections: user_id', 'Function: PARQUET_SCAN', 'Projections: user_id', "Filters: event_type = 'purchase'"]
```

The plan shows a scan of the Parquet file that projects only `user_id` and applies the filter `event_type = 'purchase'` **inside the scan**: the filter is *pushed down*, so rows are discarded while reading, not after loading everything. In pandas `read_parquet(..., columns=[...])` gives the same saving by hand; in SQL the engine decides for you.

### 9.4 Partitioned datasets

A big table is often stored as a **folder of files**, one per partition (for events: one per month). A query that filters on the partition column reads only the matching files.

```python run
con.execute(f"""
COPY (SELECT *, date_trunc('month', event_time)::DATE AS month FROM events)
TO '{tmp / 'events_by_month'}' (FORMAT parquet, PARTITION_BY (month))
""")
folders = sorted(p.name for p in (tmp / "events_by_month").iterdir())
print(folders)
files = q(f"""
SELECT DISTINCT filename
FROM read_parquet('{tmp / 'events_by_month'}/*/*.parquet', hive_partitioning = true, filename = true)
WHERE month = DATE '2025-03-01'
""")
print("files read for March only:", len(files), "->", pathlib.Path(files.iloc[0, 0]).parent.name)
print(q(f"SELECT COUNT(*) AS march_events FROM read_parquet('{tmp / 'events_by_month'}/*/*.parquet', hive_partitioning = true) WHERE month = DATE '2025-03-01'").to_string(index=False))
```
```text
['month=2025-01-01', 'month=2025-02-01', 'month=2025-03-01', 'month=2025-04-01', 'month=2025-05-01', 'month=2025-06-01', 'month=2025-07-01']
files read for March only: 1 -> month=2025-03-01
 march_events
        10891
```

The folder names carry the partition value (`month=2025-03-01`). With `hive_partitioning = true`, DuckDB turns them back into a column and **prunes**: asking for March opens a single file. The design question is the partition key: choose a column that queries filter on (a date), with a moderate number of values. Partitioning by `user_id` would create thousands of tiny files and be slower, not faster.

### 9.5 CSV and persistent files

DuckDB reads CSV files with automatic detection of the delimiter, header and types. Check the types it chose, because a guess can be wrong (a ZIP code read as a number loses its leading zero: da.05):

```python run
print(q(f"SELECT * FROM read_csv('{tmp / 'events.csv'}') LIMIT 2").to_string(index=False))
print(q(f"DESCRIBE SELECT * FROM read_csv('{tmp / 'events.csv'}')")[["column_name", "column_type"]].to_string(index=False))
```
```text
 event_id  user_id          event_time event_type
        1     2804 2025-01-01 00:35:00      login
        2     1939 2025-01-01 01:55:00      login
column_name column_type
   event_id      BIGINT
    user_id      BIGINT
 event_time   TIMESTAMP
 event_type     VARCHAR
```

An in-memory database vanishes at the end of the program. To keep tables, connect to a file. A DuckDB file stores tables the same columnar way; reopening it later gives the data back.

```python run
db_path = tmp / "learnloop.duckdb"
disk = duckdb.connect(str(db_path))
disk.execute("CREATE TABLE users AS SELECT * FROM users")           # copy the DataFrame into a table
disk.execute("CREATE TABLE orders AS SELECT * FROM orders")
disk.close()
again = duckdb.connect(str(db_path), read_only=True)
print(again.execute("SELECT COUNT(*) FROM users").fetchone()[0], "users;", again.execute("SELECT SUM(amount) FROM orders").fetchone()[0], "revenue")
again.close()
```
```text
4000 users; 1037303 revenue
```

Use a file when the data are loaded once and queried many times; use the in-memory database plus Parquet files when the files are the source of truth.

### 9.6 Speed: DuckDB against pandas

How big is "big"? Build a table of 3 million rows with random numbers and time the same groupby in both tools. The timings are **machine-specific**: read the ratio, not the seconds.

```python run
import time
rng = np.random.default_rng(1)
n = 3_000_000
bigdf = pd.DataFrame({"user_id": rng.integers(1, 200_000, n), "country": rng.choice(["IN", "US", "UK", "DE", "FR"], n),
                      "amount": rng.exponential(100, n).round(2)})


def best_of(fn, repeat=3):
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return min(times)


t_pd = best_of(lambda: bigdf.groupby("country").agg(n=("user_id", "nunique"), total=("amount", "sum"), top=("amount", "max")))
t_dd = best_of(lambda: duckdb.sql("SELECT country, COUNT(DISTINCT user_id) AS n, SUM(amount) AS total, MAX(amount) AS top FROM bigdf GROUP BY country").df())
print(f"pandas : {t_pd * 1000:8.1f} ms   (machine-specific)")
print(f"duckdb : {t_dd * 1000:8.1f} ms   (machine-specific)")
a = bigdf.groupby("country")["amount"].sum().sort_index()
b = duckdb.sql("SELECT country, SUM(amount) AS s FROM bigdf GROUP BY country ORDER BY country").df().set_index("country")["s"]
print("same totals:", bool(np.allclose(a.to_numpy(), b.to_numpy())))
```
```text
pandas :    318.5 ms   (machine-specific)
duckdb :    220.4 ms   (machine-specific)
same totals: True
```

For this query the two tools are close: pandas' `nunique` is well optimised, and the machine here has a limited number of cores. Do not conclude that the engine does not matter. The gap opens in two other situations. First, when the data **start in a file**: DuckDB reads only the columns the query needs, straight from Parquet, while pandas reads the whole file first.

```python run
bigdf.to_parquet(tmp / "big.parquet")
t_pd_file = best_of(lambda: pd.read_parquet(tmp / "big.parquet").groupby("country")["amount"].sum(), repeat=3)
t_dd_file = best_of(lambda: duckdb.sql(f"SELECT country, SUM(amount) FROM '{tmp / 'big.parquet'}' GROUP BY country").df(), repeat=3)
print(f"pandas, read the file then group : {t_pd_file * 1000:8.1f} ms   (machine-specific)")
print(f"duckdb, query the file directly  : {t_dd_file * 1000:8.1f} ms   (machine-specific)")
```
```text
pandas, read the file then group :    209.1 ms   (machine-specific)
duckdb, query the file directly  :     25.8 ms   (machine-specific)
```

Second, when the data **do not fit in memory**: DuckDB can query a Parquet file larger than your RAM by reading it in pieces, where `pd.read_parquet` fails. On a few thousand rows nobody notices any of this. The lesson: *measure your own query on your own data* (several runs, best of them), and check the answers too; the line before compared the totals.

> **Predict the output.** If the groupby used `SUM(amount)` over a float column and you compare the two tools with `==` instead of `np.allclose`, would you expect the totals to be bit-for-bit identical?

<details><summary>Answer</summary>

```python run
exact = bool((a.to_numpy() == b.to_numpy()).all())
print("bitwise identical:", exact)
print("largest relative difference:", float(np.max(np.abs(a.to_numpy() - b.to_numpy()) / a.to_numpy())))
```
```text
bitwise identical: False
largest relative difference: 3.4775961706602177e-15
```

Floating-point addition is not associative: adding three million numbers in a different order (parallel chunks in DuckDB, a pairwise scheme in pandas) gives results that differ in the last digits. The differences are around 1e-15 or smaller: harmless, but a test that uses `==` on float sums will fail without any bug. Compare floats with a tolerance (`np.allclose`, `abs(a - b) < 1e-9`), as we did in da.06 (`both_ways`), and keep money in integers or `DECIMAL` types when exactness matters.

</details>

## 10. Checking your SQL

A query that runs is not a query that is right. The checks of da.06 have SQL forms.

### 10.1 Assertions on grain and counts

```python run
def assert_grain(sql, key, label=""):
    """The result of `sql` must have exactly one row per `key`."""
    df = q(sql)
    n_rows, n_keys = len(df), len(df.drop_duplicates(subset=key))
    if n_rows != n_keys:
        raise AssertionError(f"{label}: {n_rows} rows but only {n_keys} distinct {key}: the grain is wrong")
    print(f"{label}: {n_rows} rows, one per {key} OK")
    return df


assert_grain("SELECT user_id, MIN(event_time) AS first_login FROM events WHERE event_type = 'login' GROUP BY 1", ["user_id"], "first login per user")
try:
    assert_grain("SELECT u.user_id, o.order_id FROM users u LEFT JOIN orders o USING (user_id)", ["user_id"], "users joined to orders")
except AssertionError as e:
    print("AssertionError:", e)
```
```text
first login per user: 4000 rows, one per ['user_id'] OK
AssertionError: users joined to orders: 4036 rows but only 4000 distinct ['user_id']: the grain is wrong
```

The second query is the fan-out of da.06 in SQL: a left join from users to orders gives one row per order, so the claim "one row per user" is false for the 36 users who bought twice, and the assertion says so.

### 10.2 A second engine

Compute the same table with pandas and compare. Here is the retention matrix of section 6, re-derived without SQL.

```python run
cohort_m = users.assign(cohort_month=users["signup_at"].dt.to_period("M").dt.to_timestamp())
login = events[(events["event_type"] == "login") & (events["event_time"] < "2025-07-01")]
am = (login.assign(month=login["event_time"].dt.to_period("M").dt.to_timestamp())[["user_id", "month"]].drop_duplicates())
j = am.merge(cohort_m[["user_id", "cohort_month"]], on="user_id", validate="m:1")
j["k"] = (j["month"].dt.year - j["cohort_month"].dt.year) * 12 + (j["month"].dt.month - j["cohort_month"].dt.month)
counts = j.groupby(["cohort_month", "k"])["user_id"].nunique().unstack()
sizes = cohort_m.groupby("cohort_month").size()
pandas_matrix = counts.div(sizes, axis=0).mul(100).round(1)

sql_matrix = retention.pivot(index="cohort_month", columns="k", values="retention_pct")
sql_matrix.index = pd.to_datetime(sql_matrix.index)
pandas_matrix.columns = sql_matrix.columns
diff = (pandas_matrix - sql_matrix).abs().to_numpy()
print("largest difference between SQL and pandas matrices:", float(np.nanmax(diff)))
print("NaN pattern identical:", bool((pandas_matrix.isna().to_numpy() == sql_matrix.isna().to_numpy()).all()))
```
```text
largest difference between SQL and pandas matrices: 0.0
NaN pattern identical: True
```

Two independent routes give the same triangle, with the same empty cells. If they disagreed, the first suspect would be the definition of `k` (boundaries against elapsed time) or the filter on complete months.

### 10.3 A test with a tiny table

The strongest test is a table so small that you can compute the answer by hand. Wrap the query in a function and call it on a fixture with known retention.

```python run
RETENTION_SQL = """
WITH cohort AS (SELECT user_id, date_trunc('month', signup_at)::DATE AS cohort_month FROM users),
size AS (SELECT cohort_month, COUNT(*) AS n FROM cohort GROUP BY 1),
act AS (SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS m FROM events WHERE event_type = 'login' AND event_time < TIMESTAMP '{cutoff}'),
cnt AS (SELECT c.cohort_month, date_diff('month', c.cohort_month, a.m) AS k, COUNT(DISTINCT c.user_id) AS active
        FROM cohort c JOIN act a USING (user_id) GROUP BY 1, 2)
SELECT cohort_month, k, active, n, active * 100.0 / n AS pct FROM cnt JOIN size USING (cohort_month) ORDER BY 1, 2
"""


def retention_on(test_users, test_events, cutoff):
    t = duckdb.connect()
    t.register("users", test_users)
    t.register("events", test_events)
    return t.execute(RETENTION_SQL.format(cutoff=cutoff)).df()


tu = pd.DataFrame({"user_id": [1, 2, 3, 4], "signup_at": pd.to_datetime(["2025-01-05", "2025-01-20", "2025-01-25", "2025-02-02"])})
te = pd.DataFrame({"user_id": [1, 1, 1, 2, 3, 3, 4], "event_type": "login",
                   "event_time": pd.to_datetime(["2025-01-05", "2025-02-03", "2025-02-20",     # user 1: Jan, Feb, Feb (two logins in Feb)
                                                 "2025-01-20",                                   # user 2: Jan only
                                                 "2025-01-25", "2025-03-01",                     # user 3: Jan, Mar (skips Feb)
                                                 "2025-02-02"])})                                # user 4: Feb only
res = retention_on(tu, te, "2025-04-01")
print(res.assign(pct=res["pct"].round(1)).to_string(index=False))
expected = {("2025-01-01", 0): 3, ("2025-01-01", 1): 1, ("2025-01-01", 2): 1, ("2025-02-01", 0): 1}
got = {(str(r.cohort_month)[:10], int(r.k)): int(r.active) for r in res.itertuples()}
assert got == expected, got
print("hand-computed expectations match")
```
```text
cohort_month  k  active  n    pct
  2025-01-01  0       3  3 100.00
  2025-01-01  1       1  3  33.30
  2025-01-01  2       1  3  33.30
  2025-02-01  0       1  1 100.00
hand-computed expectations match
```

By hand: the January cohort has three users (1, 2, 3). In January, all three were active (k = 0). In February only user 1 (k = 1), who logged in **twice** and still counts once. In March only user 3 (k = 2), who skipped February, so the February cell does not include them and March does. The February cohort is user 4 alone. The test asserts exactly these counts. A fixture like this catches the three classic bugs: counting logins instead of users (user 1 would count 2 in February), mis-indexing `k` (user 3 would appear in the wrong column), and the lost `DISTINCT`.

### 10.4 Style that prevents bugs

| Habit | Why |
|---|---|
| One idea per CTE, named for its content | each step can be run and checked alone |
| A grain comment on every CTE | the reader (and you) can verify joins |
| Explicit column lists in the final `SELECT` | `SELECT *` hides a column that changed or duplicated |
| `USING (key)` or an explicit `ON` | no accidental cross join |
| Constants such as dates in one place | the same cutoff everywhere (use a CTE or a parameter) |
| Parameters with `?`, never string pasting | no injection, no quoting bugs |
| Check row counts after every join | fan-out is silent |
| Keep a hand-checked fixture | the only real proof |

## 11. Project: business questions answered in SQL

**The brief.** The LearnLoop leadership asks ten questions. Answer each with **one SQL file**, run them all from Python, save the results, and verify at least three with an independent method. The data are the three tables of this chapter, complete up to 15 July 2025.

Each query carries its definition at the top, in the comments, as you practised in da.06. They are kept in a dictionary so that a single loop runs, times and saves them.

```python run
QUESTIONS = {}

QUESTIONS["q01_weekly_signups"] = """
-- Q1  How many users sign up per week, and how fast is it growing?
-- Grain: week (Monday start). Complete weeks only: the first and the last week of the data are partial.
WITH w AS (SELECT date_trunc('week', signup_at)::DATE AS week, COUNT(*) AS signups FROM users GROUP BY 1)
SELECT week, signups, signups - lag(signups) OVER (ORDER BY week) AS change,
       ROUND((signups - lag(signups) OVER (ORDER BY week)) * 100.0 / NULLIF(lag(signups) OVER (ORDER BY week), 0), 1) AS growth_pct
FROM w WHERE week >= DATE '2025-01-06' AND week < DATE '2025-06-30' ORDER BY week
"""

QUESTIONS["q02_mau_stickiness"] = """
-- Q2  Monthly active users and stickiness (average DAU / MAU), complete months only.
-- Active = at least one login in the period.
WITH l AS (SELECT DISTINCT user_id, event_time::DATE AS day FROM events WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01'),
dau AS (SELECT day, COUNT(*) AS users FROM l GROUP BY day),
m AS (SELECT date_trunc('month', day)::DATE AS month, COUNT(DISTINCT user_id) AS mau FROM l GROUP BY 1),
a AS (SELECT date_trunc('month', day)::DATE AS month, AVG(users) AS avg_dau FROM dau GROUP BY 1)
SELECT month, mau, ROUND(avg_dau, 1) AS avg_dau, ROUND(avg_dau * 100.0 / mau, 1) AS stickiness_pct FROM m JOIN a USING (month) ORDER BY month
"""

QUESTIONS["q03_cohort_retention"] = """
-- Q3  Monthly cohort retention. Cohort = signup month. Active = login in the calendar month.
-- Grain: cohort and month index k. Cells exist only for complete months (before 1 July).
WITH cohort AS (SELECT user_id, date_trunc('month', signup_at)::DATE AS cohort_month FROM users),
size AS (SELECT cohort_month, COUNT(*) AS n FROM cohort GROUP BY 1),
act AS (SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS m FROM events WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01'),
cnt AS (SELECT c.cohort_month, date_diff('month', c.cohort_month, a.m) AS k, COUNT(DISTINCT c.user_id) AS active FROM cohort c JOIN act a USING (user_id) GROUP BY 1, 2)
SELECT cohort_month, MAX(n) AS size,
       ROUND(MAX(active) FILTER (WHERE k = 1) * 100.0 / MAX(n), 1) AS m1, ROUND(MAX(active) FILTER (WHERE k = 2) * 100.0 / MAX(n), 1) AS m2,
       ROUND(MAX(active) FILTER (WHERE k = 3) * 100.0 / MAX(n), 1) AS m3, ROUND(MAX(active) FILTER (WHERE k = 4) * 100.0 / MAX(n), 1) AS m4,
       ROUND(MAX(active) FILTER (WHERE k = 5) * 100.0 / MAX(n), 1) AS m5
FROM cnt JOIN size s USING (cohort_month) GROUP BY cohort_month ORDER BY cohort_month
"""

QUESTIONS["q04_channel_quality"] = """
-- Q4  Which channel brings the best users? Month-1 retention (cohorts Jan-May), buyers, revenue per user.
-- Grain: channel. Users: all who signed up before 1 June (a complete month 1).
WITH base AS (SELECT user_id, channel, date_trunc('month', signup_at)::DATE AS cm FROM users WHERE signup_at < TIMESTAMP '2025-06-01'),
m1 AS (SELECT DISTINCT e.user_id FROM events e JOIN base b USING (user_id)
       WHERE e.event_type = 'login' AND date_trunc('month', e.event_time)::DATE = b.cm + INTERVAL 1 MONTH),
rev AS (SELECT user_id, SUM(amount) AS revenue, COUNT(*) AS orders FROM orders GROUP BY 1)
SELECT b.channel, COUNT(*) AS users, ROUND(COUNT(m1.user_id) * 100.0 / COUNT(*), 1) AS m1_retention_pct,
       COUNT(r.user_id) AS buyers, ROUND(COUNT(r.user_id) * 100.0 / COUNT(*), 1) AS buyer_pct,
       ROUND(COALESCE(SUM(r.revenue), 0) * 1.0 / COUNT(*), 0) AS revenue_per_user
FROM base b LEFT JOIN m1 USING (user_id) LEFT JOIN rev r USING (user_id) GROUP BY b.channel ORDER BY revenue_per_user DESC
"""

QUESTIONS["q05_funnel_by_channel"] = """
-- Q5  Ordered purchase funnel by channel. Users counted once, at their first time per step; steps must happen in order.
WITH f AS (
  SELECT u.user_id, u.channel,
         MIN(e.event_time) FILTER (WHERE e.event_type = 'view_course')    AS tv,
         MIN(e.event_time) FILTER (WHERE e.event_type = 'add_to_cart')    AS tc,
         MIN(e.event_time) FILTER (WHERE e.event_type = 'checkout_start') AS tk,
         MIN(e.event_time) FILTER (WHERE e.event_type = 'purchase')       AS tp
  FROM users u LEFT JOIN events e USING (user_id) GROUP BY u.user_id, u.channel)
SELECT channel, COUNT(tv) AS viewed,
       COUNT(*) FILTER (WHERE tc >= tv) AS carted,
       COUNT(*) FILTER (WHERE tk >= tc AND tc >= tv) AS checkout,
       COUNT(*) FILTER (WHERE tp >= tk AND tk >= tc AND tc >= tv) AS purchased,
       ROUND(COUNT(*) FILTER (WHERE tp >= tk AND tk >= tc AND tc >= tv) * 100.0 / COUNT(tv), 1) AS view_to_buy_pct
FROM f GROUP BY channel ORDER BY channel
"""

QUESTIONS["q06_revenue_by_month_plan"] = """
-- Q6  Revenue by month and plan, with month-over-month growth (complete months). Revenue = sum of order amounts by order_time.
WITH r AS (SELECT date_trunc('month', order_time)::DATE AS month, plan, SUM(amount) AS revenue, COUNT(*) AS orders
           FROM orders WHERE order_time < TIMESTAMP '2025-07-01' GROUP BY 1, 2),
t AS (SELECT month, SUM(revenue) AS revenue, SUM(orders) AS orders,
             SUM(revenue) FILTER (WHERE plan = 'annual') AS annual_revenue FROM r GROUP BY 1)
SELECT month, orders, revenue, ROUND(annual_revenue * 100.0 / revenue, 1) AS annual_share_pct,
       ROUND((revenue - lag(revenue) OVER (ORDER BY month)) * 100.0 / lag(revenue) OVER (ORDER BY month), 1) AS growth_pct
FROM t ORDER BY month
"""

QUESTIONS["q07_top_spenders_per_country"] = """
-- Q7  The three biggest spenders in each country. Ties are broken by user_id so the answer is reproducible.
SELECT country, user_id, spent, rank_in_country FROM (
  SELECT u.country, o.user_id, SUM(o.amount) AS spent,
         row_number() OVER (PARTITION BY u.country ORDER BY SUM(o.amount) DESC, o.user_id) AS rank_in_country
  FROM orders o JOIN users u USING (user_id) GROUP BY u.country, o.user_id)
WHERE rank_in_country <= 3 ORDER BY country, rank_in_country
"""

QUESTIONS["q08_active_states"] = """
-- Q8  MAU split into new / retained / resurrected (complete months), with the churned from the previous month.
WITH am AS (SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS month FROM events
            WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01'),
x AS (SELECT user_id, month, lag(month) OVER (PARTITION BY user_id ORDER BY month) AS prev FROM am),
s AS (SELECT month, COUNT(*) AS mau,
             COUNT(*) FILTER (WHERE prev IS NULL) AS new_users,
             COUNT(*) FILTER (WHERE prev = month - INTERVAL 1 MONTH) AS retained,
             COUNT(*) FILTER (WHERE prev < month - INTERVAL 1 MONTH) AS resurrected FROM x GROUP BY month)
SELECT month, mau, new_users, retained, resurrected, lag(mau) OVER (ORDER BY month) - retained AS churned FROM s ORDER BY month
"""

QUESTIONS["q09_longest_streaks"] = """
-- Q9  Who has the longest run of consecutive login days? One row per user: their best streak.
WITH d AS (SELECT DISTINCT user_id, event_time::DATE AS day FROM events WHERE event_type = 'login'),
n AS (SELECT user_id, day, day - CAST(row_number() OVER (PARTITION BY user_id ORDER BY day) AS INTEGER) AS island FROM d),
st AS (SELECT user_id, MIN(day) AS first_day, MAX(day) AS last_day, COUNT(*) AS days_in_row FROM n GROUP BY user_id, island)
SELECT user_id, first_day, last_day, days_in_row FROM st QUALIFY row_number() OVER (ORDER BY days_in_row DESC, user_id) <= 5 ORDER BY days_in_row DESC, user_id
"""

QUESTIONS["q10_data_quality"] = """
-- Q10  Data-quality report: counts that should be zero, and counts that explain odd numbers.
SELECT 'events after the extraction time' AS check_name, COUNT(*) AS rows_ FROM events WHERE event_time > TIMESTAMP '2025-07-15'
UNION ALL SELECT 'events of unknown users', COUNT(*) FROM events WHERE user_id NOT IN (SELECT user_id FROM users)
UNION ALL SELECT 'orders without a purchase event', COUNT(*) FROM orders o WHERE NOT EXISTS (SELECT 1 FROM events e WHERE e.user_id = o.user_id AND e.event_type = 'purchase' AND e.event_time = o.order_time)
UNION ALL SELECT 'purchase events without an order', COUNT(*) FROM events e WHERE e.event_type = 'purchase' AND NOT EXISTS (SELECT 1 FROM orders o WHERE o.user_id = e.user_id AND o.order_time = e.event_time)
UNION ALL SELECT 'users with a purchase but no checkout (direct links)', COUNT(DISTINCT user_id) FROM events e WHERE event_type = 'purchase' AND NOT EXISTS (SELECT 1 FROM events c WHERE c.user_id = e.user_id AND c.event_type = 'checkout_start')
UNION ALL SELECT 'users whose first login is not at sign-up', COUNT(*) FROM (SELECT u.user_id FROM users u JOIN events e USING (user_id) WHERE e.event_type = 'login' GROUP BY u.user_id, u.signup_at HAVING MIN(e.event_time) <> u.signup_at)
"""

RESULTS = {}
for name, sql in QUESTIONS.items():
    RESULTS[name] = q(sql)
    print(f"{name:32} -> {RESULTS[name].shape[0]:3d} rows x {RESULTS[name].shape[1]} columns")
```
```text
q01_weekly_signups               ->  25 rows x 4 columns
q02_mau_stickiness               ->   6 rows x 4 columns
q03_cohort_retention             ->   6 rows x 7 columns
q04_channel_quality              ->   3 rows x 6 columns
q05_funnel_by_channel            ->   3 rows x 6 columns
q06_revenue_by_month_plan        ->   6 rows x 5 columns
q07_top_spenders_per_country     ->   9 rows x 4 columns
q08_active_states                ->   6 rows x 6 columns
q09_longest_streaks              ->   5 rows x 4 columns
q10_data_quality                 ->   6 rows x 2 columns
```

Every question ran. Look at four of the answers.

```python run
print(RESULTS["q03_cohort_retention"].to_string(index=False))
print()
print(RESULTS["q04_channel_quality"].to_string(index=False))
print()
print(RESULTS["q06_revenue_by_month_plan"].to_string(index=False))
```
```text
cohort_month  size    m1    m2    m3    m4    m5
  2025-01-01   644 79.00 57.50 40.70 39.00 32.30
  2025-02-01   618 75.10 55.20 44.80 36.60   NaN
  2025-03-01   730 74.10 55.20 44.50   NaN   NaN
  2025-04-01   684 77.00 51.90   NaN   NaN   NaN
  2025-05-01   709 79.30   NaN   NaN   NaN   NaN
  2025-06-01   615   NaN   NaN   NaN   NaN   NaN

 channel  users  m1_retention_pct  buyers  buyer_pct  revenue_per_user
referral    507             90.70      99      19.50            309.00
 organic   1687             81.80     299      17.70            284.00
     ads   1191             64.10     174      14.60            227.00

     month  orders    revenue  annual_share_pct  growth_pct
2025-01-01   92.00 119,408.00             70.30         NaN
2025-02-01  108.00 144,892.00             71.80       21.30
2025-03-01  130.00 208,370.00             78.70       43.80
2025-04-01  122.00 169,378.00             73.20      -18.70
2025-05-01  133.00 223,867.00             80.40       32.20
2025-06-01   98.00 139,902.00             74.30      -37.50
```

```python run
print(RESULTS["q10_data_quality"].to_string(index=False))
print()
print(RESULTS["q08_active_states"].to_string(index=False))
```
```text
                                          check_name  rows_
                    events after the extraction time      0
                             events of unknown users      0
                     orders without a purchase event      0
                    purchase events without an order      0
users with a purchase but no checkout (direct links)    133
           users whose first login is not at sign-up      0

     month  mau  new_users  retained  resurrected  churned
2025-01-01  644        644         0            0     <NA>
2025-02-01 1127        618       509            0      135
2025-03-01 1564        730       787           47      340
2025-04-01 1828        684      1039          105      525
2025-05-01 2167        709      1217          241      611
2025-06-01 2291        615      1347          329      820
```

The data-quality report is as important as the answers. Rows that must be zero are zero (nothing after the extraction time, no orphan events, orders and purchase events match one to one). The line "users with a purchase but no checkout" is **not** zero: those direct-link buyers are real and are the reason why the ordered funnel has fewer purchases than the number of buyers. A reader of the funnel must know it.

### 11.1 Verify three answers independently

A result you did not check is a claim. Check three of them with pandas.

```python run
# Q3: retention matrix already matched pandas in 10.2; here Q6 and Q8 and Q5

# Q6: revenue by month in pandas
o = orders[orders["order_time"] < "2025-07-01"]
pd_rev = o.groupby(o["order_time"].dt.to_period("M").dt.to_timestamp())["amount"].sum()
sql_rev = RESULTS["q06_revenue_by_month_plan"].set_index(pd.to_datetime(RESULTS["q06_revenue_by_month_plan"]["month"]))["revenue"]
print("Q6 revenue matches pandas       :", bool((pd_rev.to_numpy() == sql_rev.to_numpy()).all()))

# Q8: identities
s8 = RESULTS["q08_active_states"]
print("Q8 MAU = new+retained+resurrected:", bool((s8["mau"] == s8["new_users"] + s8["retained"] + s8["resurrected"]).all()))
print("Q8 MAU(m-1) = retained + churned :", bool((s8["mau"].shift(1)[1:] == (s8["retained"] + s8["churned"])[1:]).all()))

# Q5: the funnel in pandas, with ordering
first = events.pivot_table(index="user_id", columns="event_type", values="event_time", aggfunc="min")
ordered = first["purchase"].notna() & (first["purchase"] >= first["checkout_start"]) & (first["checkout_start"] >= first["add_to_cart"]) & (first["add_to_cart"] >= first["view_course"])
print("Q5 purchased (ordered), pandas   :", int(ordered.sum()), "| SQL:", int(RESULTS["q05_funnel_by_channel"]["purchased"].sum()))

# Q1: no growth figure from a partial week
q1 = RESULTS["q01_weekly_signups"]
print("Q1 weeks reported                :", len(q1), "| first:", q1["week"].iloc[0], "| last:", q1["week"].iloc[-1])
```
```text
Q6 revenue matches pandas       : True
Q8 MAU = new+retained+resurrected: True
Q8 MAU(m-1) = retained + churned : True
Q5 purchased (ordered), pandas   : 528 | SQL: 528
Q1 weeks reported                : 25 | first: 2025-01-06 00:00:00 | last: 2025-06-23 00:00:00
```

All four checks agree. Notice what Q1 does: it reports only the complete weeks; the partial week of 30 December and the last, partial week at the end of June are left out, and the definition says so.

### 11.2 Save the work

Each query becomes a `.sql` file with its definition in the header, and each result a Parquet file, so that a colleague can re-run the questions and compare.

```python run
out = tmp / "learnloop_report"
(out / "sql").mkdir(parents=True)
(out / "results").mkdir()
for name, sql in QUESTIONS.items():
    (out / "sql" / f"{name}.sql").write_text(sql.strip() + "\n")
    RESULTS[name].to_parquet(out / "results" / f"{name}.parquet", index=False)
print(sorted(p.name for p in (out / "sql").iterdir())[:4], "...")
print(len(list((out / "sql").iterdir())), "sql files,", len(list((out / "results").iterdir())), "result files")
# re-run from the files: the saved SQL must give the saved result
rerun = q((out / "sql" / "q06_revenue_by_month_plan.sql").read_text())
saved = pd.read_parquet(out / "results" / "q06_revenue_by_month_plan.parquet")
print("saved SQL reproduces the saved result:", rerun.equals(saved))
```
```text
['q01_weekly_signups.sql', 'q02_mau_stickiness.sql', 'q03_cohort_retention.sql', 'q04_channel_quality.sql'] ...
10 sql files, 10 result files
saved SQL reproduces the saved result: True
```

### 11.3 What to hand in

1. One `.sql` file per question, with the **definition in the header** (grain, date basis, complete periods, exclusions).
2. A runner (like the loop above) that executes all of them against the data and writes the results.
3. **Three independent checks**, written as code, that fail when the answer is wrong.
4. A **data-quality query** that reports the counts which should be zero.
5. For every rate: the counts behind it. For every period: whether it is complete.
6. A short note listing the **assumptions** (what active means, which time zone, what counts as a purchase) and the **known quirks** (the direct-link buyers).

## 12. Common traps

| Trap | What happens | Fix |
|---|---|---|
| Counting events when the question names users | steps 2 to 3 times too big | `COUNT(DISTINCT user_id)` at the grain of the question (1.3, 7.1) |
| Summing a window column | double counting | the grain of a window column is its partition (4.1) |
| `row_number` with ties | different rows on each run | add a tie-breaker to `ORDER BY` (4.2) |
| Default frame with `last_value` | returns the current row | spell out the frame to `UNBOUNDED FOLLOWING` (4.4) |
| `RANGE` default frame with duplicate order values | tied rows share the running total | use `ROWS`, or aggregate first (4.4) |
| Moving average over rows with missing days | "7 rows" is not "7 days" | join to a calendar, or use `RANGE ... INTERVAL` (4.5, 5.1) |
| Window function in `WHERE` | error | `QUALIFY` (DuckDB) or a subquery (4.7) |
| Gaps-and-islands without `DISTINCT` | streaks break on duplicate days | de-duplicate to the grain first (4.8) |
| Calendar missing | absent days vanish | `generate_series` and `LEFT JOIN` (5.1) |
| Distinct counts summed | users counted many times | recompute from the rows (5.2) |
| `date_diff('month', ...)` read as elapsed time | 31 January to 1 February is "1 month" | know boundaries from complete units (2.4) |
| Partial first or last period | false growth or a fake cliff | complete periods only, or label (5.3, 6.4) |
| Denominator that includes people who did not exist yet | percentages too low | restrict the denominator (3.1, 6.6) |
| `COALESCE(count, 0)` outside the valid grid | zero where the truth is "not observed" | build the grid of valid cells first (6.4) |
| Average of cohort percentages | wrong when cohort sizes differ | pool numerators and denominators (6.5) |
| Day-N retention without eligibility | recent users depress the rate | only users observed for N days (6.6) |
| Unordered funnel | skippers and bots counted | compare first times in order (7.3) |
| `LEFT JOIN` to events for a funnel | fine for users, wrong for sums | one row per user first, then count (7.2) |
| Time between steps among converters | survivorship | say who the summary describes (7.5) |
| String-pasted SQL | injection and quote bugs | `?` parameters (1.1) |
| Float totals compared with `==` | spurious mismatch | tolerance (9.6) |
| Partitioning on a high-cardinality column | thousands of tiny files | partition on a date (9.4) |
| One engine only | a logic bug goes unseen | second engine plus a hand-made fixture (10) |

A debugging habit for every wrong number in SQL: run each CTE alone, print its row count and grain, then remove joins until the number is right and add them back one at a time.

## 13. Summary

- **Window functions** compute across related rows without collapsing them. `PARTITION BY` sets the group, `ORDER BY` the order, the **frame** the neighbours. Know the ranking functions and their ties, `lag`/`lead`/`first_value`, the default frame (and why `last_value` and ties surprise people), `ROWS` against `RANGE`, running totals, moving averages, shares of the total, top-N with `QUALIFY` or a subquery, gaps and islands, and sessions by "flag, cumulative sum, group".
- **CTEs** turn a query into a recipe: one idea each, a grain comment each, checked one at a time. A denominator is a decision; name it.
- **Dates and calendars**: `date_trunc`, `date_diff` (boundaries, not elapsed time), a `generate_series` spine for missing days, complete periods only.
- **Cohort retention**: define the cohort, the activity, the month index, the numerator (distinct users) and the denominator (cohort size). Produce a long table, pivot it, and keep cells for months that have not happened **empty**: zero means "observed and nobody", missing means "not observed yet". Pool curves by adding numerators and denominators, show how many cohorts support each point, and restrict day-N retention to eligible users. This is the outcome of the chapter: you can build a cohort retention table in SQL, correctly.
- **Funnels** count users at their first time per step, in order, with the counts behind each percentage; segment them and name the group that every time summary describes. **New, retained, resurrected and churned** users decompose MAU, and two identities check the query.
- **DuckDB** queries DataFrames, CSV and Parquet directly and returns pandas, Arrow or Polars; Parquet keeps types, is small, and lets the engine read only what the query needs; partitioned folders are pruned by filters; a persistent file keeps tables. It is fast on millions of rows and can go beyond memory. Compare floats with a tolerance.
- **Check your SQL**: assert grain and counts, re-derive with a second engine, and test with a tiny table whose answer you computed by hand.
- Everything of da.06 applies in SQL: grain, fan-out, denominators, date basis, complete periods, and the habit of showing the counts behind every rate.

You reached the outcome of this chapter: you can **build a cohort retention table in SQL**, with the right definitions, the right denominators, the empty cells where they belong, and independent checks that prove it. Next, da.08 turns from counting to inference: statistical reasoning for analysts (distributions, sampling, uncertainty, confidence intervals and tests), which gives you the tools to say how sure a difference between two cohorts or channels really is.
