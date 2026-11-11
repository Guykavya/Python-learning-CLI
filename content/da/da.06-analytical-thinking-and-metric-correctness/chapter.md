# Chapter 6 (DA): Analytical thinking and metric correctness

A manager asks: "How many jobs did we do in February?" You answer 895. Another analyst, looking at a different dashboard, answers 820. A third person, running a SQL query, says 807. All three numbers are *correct*. All three come from the same database. And the manager now trusts none of you.

This is the most common failure in data work, and it is almost never a coding mistake. It is a **thinking** mistake: the three people did not mean the same thing by "jobs" (created? started? completed?), by "February" (in which time zone?), or by "did" (including the cancelled ones?). The code in this chapter is short. The skill is to ask the right questions *before* you write it, and to be able to trace any total, record by record, until two numbers that disagree are explained.

By the end of this chapter you reach three outcomes: **you can state the grain of any table before analysing it**, **you can write an unambiguous metric definition**, and **you can trace a total mismatch down to the individual records that cause it**. The last one is the skill that makes people ask you, and not someone else, when the numbers do not add up.

Prerequisites: da.04 (groupby, merge, fan-out and the `safe_merge` habit) and shared.01 (SQL foundations: joins, `GROUP BY`, `NULL`). In da.04 you met fan-out and wrote `safe_merge`; here the theory behind it is complete and applied to business metrics. We use the standard library `sqlite3` for the SQL parts: no server, no internet.

> **Offline rule for this chapter.** pandas and NumPy are installed in the course environment, and `sqlite3` comes with Python. Every dataset is **synthetic**: built in code with seeded random numbers (`numpy.random.default_rng`), so you get the same numbers I did. The company, its customers and its prices are invented; the *structure* (jobs with a lifecycle, line items, payments, refunds, timestamps in UTC) is the structure of real service and e-commerce data. Every output block below was produced by running the code above it, in one session from top to bottom. **Timings and versions are machine-specific.** Some blocks show an error on purpose; for errors we print only the last line. These are the versions used:

```python run
import sys, sqlite3
import numpy as np
import pandas as pd

print("python ", sys.version.split()[0])
print("pandas ", pd.__version__)
print("numpy  ", np.__version__)
print("sqlite ", sqlite3.sqlite_version)
```
```text
python  3.14.4
pandas  3.1.1
numpy   2.5.4
sqlite  3.46.1
```

Two setup lines make the printed tables compact.

```python run
pd.set_option("display.width", 110)
pd.set_option("display.max_columns", 12)
pd.set_option("display.max_rows", 14)
pd.set_option("display.float_format", "{:,.2f}".format)
print("display options set")
```
```text
display options set
```

## Table of contents

1. [One question, three answers](#1-one-question-three-answers)
2. [Grain: what one row represents](#2-grain-what-one-row-represents)
3. [Keys and how to test them](#3-keys-and-how-to-test-them)
4. [Join fan-out](#4-join-fan-out)
5. [Counting: rows, values, distinct values](#5-counting-rows-values-distinct-values)
6. [Averages: simple, weighted, and Simpson's paradox](#6-averages-simple-weighted-and-simpsons-paradox)
7. [Metric definitions](#7-metric-definitions)
8. [Dates: the basis of a metric](#8-dates-the-basis-of-a-metric)
9. [Status and lifecycle](#9-status-and-lifecycle)
10. [The same questions in SQL](#10-the-same-questions-in-sql)
11. [Reconciliation: from a total to the records](#11-reconciliation-from-a-total-to-the-records)
12. [Worked case: total volume against completed plus pending](#12-worked-case-total-volume-against-completed-plus-pending)
13. [A reusable toolkit](#13-a-reusable-toolkit)
14. [Project: metric definitions and a reconciliation report](#14-project-metric-definitions-and-a-reconciliation-report)
15. [Common traps](#15-common-traps)
16. [Summary](#16-summary)

## 1. One question, three answers

### 1.1 The business

Our synthetic company, **QuickFix**, connects customers with technicians for home and office repair jobs. A customer **creates** a job on the app. A technician is booked, and later **starts** the job on site. When the work is done, the job is **completed**. Some jobs are **cancelled** before they start, some **fail**, and the newest ones are still **pending**. A job has **line items** (labour, parts, travel), the customer makes one or two **payments**, and a few jobs get a **refund**.

All timestamps are stored in **UTC** (the world standard time). The company works in India, where local time (IST) is UTC plus 5 hours 30 minutes. The data were extracted at the start of **5 April 2025** (UTC). Here is the data factory. You need not study the code; read the comments, which list the facts we rely on.

```python run
CUT = pd.Timestamp("2025-04-05 00:00")            # when the data were extracted (UTC)


def make_business(seed=3, n=3000):
    rng = np.random.default_rng(seed)
    customers = pd.DataFrame({
        "customer_id": np.arange(1, 801),
        "city": rng.choice(["Pune", "Delhi", "Mumbai", "Jaipur"], 800, p=[.25, .35, .3, .1]),
        "segment": rng.choice(["home", "business"], 800, p=[.8, .2]),
    })
    created = pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 90 * 24 * 60, n), unit="min")
    jobs = pd.DataFrame({"job_id": np.arange(5001, 5001 + n),
                         "customer_id": rng.integers(1, 801, n), "created_at": created})
    # when does work start? usually within 2-3 days; 20% are booked 3 to 14 days ahead
    lag_h = np.where(rng.random(n) < .2, rng.uniform(72, 14 * 24, n), rng.gamma(2, 24, n))
    start = jobs["created_at"] + pd.to_timedelta(lag_h, unit="h")
    end = start + pd.to_timedelta(rng.uniform(1, 6, n), unit="h")
    u = rng.random(n)
    cancelled, failed = u < .08, (u >= .08) & (u < .10)
    jobs["status"] = np.where(cancelled, "cancelled", np.where(failed, "failed",
                              np.where(end <= CUT, "completed", "pending")))
    jobs["started_at"] = start.where(~cancelled & (start <= CUT))          # actual start; empty if not started yet
    jobs["completed_at"] = end.where(jobs["status"] == "completed")
    jobs["cancelled_at"] = (jobs["created_at"] + pd.to_timedelta(rng.uniform(1, 40, n), unit="h")).where(cancelled)
    # line items: one labour line, 0-2 parts lines, sometimes a travel line
    rows = []
    for jid in jobs["job_id"]:
        rows.append((jid, 1, "labour", int(rng.integers(5, 30)) * 100))
        rows += [(jid, 2 + k, "parts", int(rng.integers(2, 20)) * 100) for k in range(rng.integers(0, 3))]
        if rng.random() < .5:
            rows.append((jid, 9, "travel", int(rng.integers(1, 4)) * 100))
    items = pd.DataFrame(rows, columns=["job_id", "line_no", "item", "amount"])
    jobs = jobs.merge(items.groupby("job_id")["amount"].sum().rename("quote_total"), on="job_id")
    # payments: completed jobs pay once (80%) or as deposit + balance (20%); some pending jobs paid a deposit
    pay = []
    pid = 9001
    for r in jobs.itertuples():
        if r.status == "completed":
            if rng.random() < .8:
                pay.append((pid, r.job_id, r.completed_at + pd.Timedelta(hours=float(rng.uniform(0, 48))), r.quote_total, "full"))
                pid += 1
            else:
                dep = round(r.quote_total * .3)
                pay.append((pid, r.job_id, r.created_at + pd.Timedelta(hours=1), dep, "deposit"))
                pay.append((pid + 1, r.job_id, r.completed_at + pd.Timedelta(hours=float(rng.uniform(0, 48))), r.quote_total - dep, "balance"))
                pid += 2
        elif r.status == "pending" and rng.random() < .3:
            pay.append((pid, r.job_id, r.created_at + pd.Timedelta(hours=1), round(r.quote_total * .3), "deposit"))
            pid += 1
    payments = pd.DataFrame(pay, columns=["payment_id", "job_id", "paid_at", "amount", "kind"])
    done = jobs[jobs["status"] == "completed"].sample(frac=.05, random_state=2)
    refunds = pd.DataFrame({"refund_id": np.arange(1, len(done) + 1), "job_id": done["job_id"].values,
                            "refunded_at": (done["completed_at"] + pd.Timedelta(days=3)).values,
                            "amount": (done["quote_total"] * rng.choice([.2, .5, 1.0], len(done))).round().values})
    return customers, jobs, items, payments, refunds


customers, jobs, items, payments, refunds = make_business()
for name, t in [("customers", customers), ("jobs", jobs), ("items", items), ("payments", payments), ("refunds", refunds)]:
    print(f"{name:10} {t.shape}")
print(jobs.head(4).to_string())
```
```text
customers  (800, 3)
jobs       (3000, 8)
items      (7554, 4)
payments   (3236, 5)
refunds    (134, 4)
   job_id  customer_id          created_at     status                    started_at                  completed_at                  cancelled_at  quote_total
0    5001          229 2025-01-19 23:55:00  completed 2025-02-02 21:58:11.571412201 2025-02-03 01:46:38.548171749                           NaT         3800
1    5002           35 2025-03-07 21:39:00  cancelled                           NaT                           NaT 2025-03-08 17:39:17.331657462          800
2    5003          142 2025-03-31 19:20:00  completed 2025-04-01 07:49:16.252140580 2025-04-01 12:24:42.202002737                           NaT         2600
3    5004          539 2025-03-30 04:33:00  completed 2025-03-31 17:33:37.881595972 2025-03-31 20:35:49.379199938                           NaT         2500
```

Five tables. `jobs` has one row per job and the timestamps of its life: `created_at`, `started_at`, `completed_at`, `cancelled_at`. A `NaT` (not a time) means "that has not happened". Look at what is missing and where: that is information, as you learned in da.05.

### 1.2 The three numbers

Three analysts each answer "how many jobs in February?" with a perfectly sensible query.

```python run
feb = lambda s: (s >= "2025-02-01") & (s < "2025-03-01")      # a half-open month: includes Feb 1, excludes Mar 1

a = int(feb(jobs["created_at"]).sum())
b = int(feb(jobs["started_at"]).sum())
c = int((feb(jobs["completed_at"])).sum())
print("A  jobs created in February     :", a)
print("B  jobs started in February     :", b)
print("C  jobs completed in February   :", c)
```
```text
A  jobs created in February     : 895
B  jobs started in February     : 820
C  jobs completed in February   : 807
```

Three numbers, 895, 820 and 807, from one table. Each is the answer to a different question. Nobody made an error, and yet a manager who sees two of them on two slides will conclude that somebody did.

The same trouble appears when one number is supposed to be the sum of others. A finance dashboard shows, for February, "completed" and "pending" next to a "total". Let us see whether the parts add up.

```python run
total = int(feb(jobs["created_at"]).sum())                                    # total volume: by created_at
completed = int((feb(jobs["started_at"]) & (jobs["status"] == "completed")).sum())   # completed volume: by started_at
pending = int((feb(jobs["started_at"]) & (jobs["status"] == "pending")).sum())       # pending volume: by started_at
print("total volume (created in Feb)          :", total)
print("completed volume (started in Feb)      :", completed)
print("pending volume (started in Feb)        :", pending)
print("completed + pending                    :", completed + pending)
print("difference from the total              :", total - completed - pending)
```
```text
total volume (created in Feb)          : 895
completed volume (started in Feb)      : 809
pending volume (started in Feb)        : 0
completed + pending                    : 809
difference from the total              : 86
```

The parts do not add up to the total: 895 against 809, a gap of 86 jobs. Note also that the pending line is **zero**, not small: a pending job has not started, so it has no `started_at`, and a filter on `started_at` can never select it. The gap is not a bug in pandas. It is the result of **different date bases** (created against started), **statuses that are left out** (cancelled and failed), and **a status that has no start date** (pending jobs that have not started). Sections 2 to 11 give you the tools; section 12 closes this case exactly, record by record.

> **Predict the output.** Before you read on, guess: which of these three effects explains most of the 86 missing jobs? (1) cancelled and failed jobs, (2) jobs created in February but started in March, (3) pending jobs with no start date.

<details><summary>Answer</summary>

There is no way to know without counting, and that is the point of the chapter. Section 12 gives the exact split. As a hint: cancelled jobs are about 8 percent of the jobs created in February, which is already more than 70 jobs. But note that jobs created in January and started in February also *add* to the completed count, so the effects partly cancel. **A net difference of 86 hides effects that are bigger in both directions.** This is why we do not stop at the net gap: we build a bridge that lists every effect.

</details>

## 2. Grain: what one row represents

### 2.1 The definition

The **grain** of a table is the answer to the question: *what does one row represent?* Not what the columns are, not what the table is called, but exactly what real-world thing or event has one row.

A grain is a sentence, and a good one has the shape "**one row per ___**", sometimes with a time part: "one row per **customer per month**". Look at our tables:

| Table | Grain (one row per...) | Key |
|---|---|---|
| `customers` | customer | `customer_id` |
| `jobs` | job | `job_id` |
| `items` | line item inside a job | `job_id` + `line_no` |
| `payments` | payment | `payment_id` |
| `refunds` | refund | `refund_id` |

You must be able to write this sentence **before** you compute anything. If you cannot, you are not ready to count, sum or join.

### 2.2 Why grain decides everything

Every statistic is a function of the grain. `len(df)` counts rows. If the rows are jobs, that is the number of jobs. If the rows are line items, it is the number of line items, which is a different number, and nothing in the code warns you.

```python run
print("rows in jobs :", len(jobs), "  <- the number of jobs")
print("rows in items:", len(items), "  <- the number of line items, NOT jobs")
print("rows in payments:", len(payments), " <- the number of payments, NOT paid jobs")
print("jobs with at least one payment:", payments["job_id"].nunique())
```
```text
rows in jobs : 3000   <- the number of jobs
rows in items: 7554   <- the number of line items, NOT jobs
rows in payments: 3236  <- the number of payments, NOT paid jobs
jobs with at least one payment: 2690
```

Three tables, three different "row counts". A dashboard that says "7,554 jobs" because someone counted rows in `items` is wrong by a factor of 2.5. The error would not be visible in any chart; it would only be visible to someone who asks, "what is one row?".

The sum has the same trap. Suppose we want the total quoted value of all jobs. The column `quote_total` lives at the **job** grain, one value per job. If we put it on the **line item** grain by a join, each job's total is repeated once per line.

```python run
right = jobs["quote_total"].sum()
wrong = items.merge(jobs[["job_id", "quote_total"]], on="job_id")["quote_total"].sum()
print("total quote, job grain (right)         :", f"{right:,}")
print("total quote, repeated on item rows     :", f"{wrong:,}")
print("inflation factor                       :", round(wrong / right, 2))
print("sum of the line amounts (also right)   :", f"{items['amount'].sum():,}")
```
```text
total quote, job grain (right)         : 8,557,500
total quote, repeated on item rows     : 23,742,100
inflation factor                       : 2.77
sum of the line amounts (also right)   : 8,557,500
```

Sums over `items["amount"]` are correct because `amount` is a property of a line item. Sums over `quote_total` are correct only on the `jobs` table. **A column has a grain too: the grain of the table it was born in.** Whenever you move a column to a table with a finer grain, its values are repeated, and a sum or a count over it is multiplied. This single rule explains most wrong dashboard numbers.

### 2.3 Different kinds of grain

Most tables fall into one of four shapes. Naming the shape tells you what to expect.

| Shape | One row is... | Example here | Watch out for |
|---|---|---|---|
| **Entity** | a thing that exists | `customers`, `jobs` | rows change over time (status updates) |
| **Event / transaction** | something that happened | `payments`, `refunds` | an entity can have many events |
| **Line / detail** | a part of a bigger record | `items` | the header's values are repeated on each line |
| **Snapshot** | the state of a thing at a moment | "jobs by status at midnight" | the same entity appears once per snapshot date |

A snapshot table is the one that surprises people most. A table "daily balance per account" has one row per account **per day**. Counting its rows gives account-days, not accounts; counting accounts needs `nunique`.

### 2.4 Stating and testing the grain

Writing the grain is the first half; **testing** it is the second. A claim "one row per job" means no `job_id` appears twice. Pandas tests it in one line:

```python run
def check_grain(df, key, name=""):
    """Does the table really have one row per `key`? Report instead of guessing."""
    key = [key] if isinstance(key, str) else list(key)
    n_rows = len(df)
    n_keys = len(df.drop_duplicates(subset=key))
    n_null = int(df[key].isna().any(axis=1).sum())
    ok = (n_rows == n_keys) and n_null == 0
    print(f"{name:10} key={key}: rows={n_rows}, distinct keys={n_keys}, null keys={n_null} -> {'OK' if ok else 'NOT UNIQUE'}")
    return ok


check_grain(customers, "customer_id", "customers")
check_grain(jobs, "job_id", "jobs")
check_grain(items, ["job_id", "line_no"], "items")
check_grain(items, "job_id", "items")
check_grain(payments, "payment_id", "payments")
check_grain(payments, "job_id", "payments")
```
```text
customers  key=['customer_id']: rows=800, distinct keys=800, null keys=0 -> OK
jobs       key=['job_id']: rows=3000, distinct keys=3000, null keys=0 -> OK
items      key=['job_id', 'line_no']: rows=7554, distinct keys=7554, null keys=0 -> OK
items      key=['job_id']: rows=7554, distinct keys=3000, null keys=0 -> NOT UNIQUE
payments   key=['payment_id']: rows=3236, distinct keys=3236, null keys=0 -> OK
payments   key=['job_id']: rows=3236, distinct keys=2690, null keys=0 -> NOT UNIQUE
```

Notice the two wrong claims: `items` by `job_id` alone, and `payments` by `job_id` alone. Both fail, and the report says how many rows exceed the distinct keys. A table can have a composite key (two columns together), and each column alone is not unique. Making `check_grain` a habit takes five seconds per table and prevents the largest class of errors in this chapter.

Notice also the count of **null keys**: a missing key can never be unique in any meaningful way, because "missing" is not an identity.

> **Try it.** `refunds` should have at most one refund per job in a simple business, but real refunds can be partial and repeated. Test whether `job_id` is unique in `refunds`. What would it mean for a metric called "refund rate" if the answer were no?

<details><summary>Answer</summary>

```python run
check_grain(refunds, "job_id", "refunds")
print("jobs with a refund:", refunds["job_id"].nunique(), " refund rows:", len(refunds))
```
```text
refunds    key=['job_id']: rows=134, distinct keys=134, null keys=0 -> OK
jobs with a refund: 134  refund rows: 134
```

In this data, each job has at most one refund, so the key is unique. If it were not, "refund rate" would have to say whether it means refunds per job (a count of **rows**) or the share of jobs that have **any** refund (a count of **distinct jobs**). The two diverge as soon as a job can be refunded twice. This is why the metric definition in section 7 names the thing it counts.

</details>

### 2.5 The grain of a result

The same question applies to *results*. A `groupby` result has the grain of its group keys. A pivot table "revenue by city and month" has one row per city and the columns are months. You should be able to state the grain of every intermediate table in your analysis, including those you do not save. When a join, a filter or a groupby changes the grain, write it in a comment: `# grain: one row per job`. After a month, those comments are worth more than the code.

## 3. Keys and how to test them

### 3.1 Primary keys, foreign keys

A **primary key** identifies one row of its table: `jobs.job_id`. A **foreign key** is a column that points to the primary key of another table: `jobs.customer_id` points to `customers.customer_id`. The pair defines how tables connect: *one customer, many jobs*. In shared.01 you met these as database constraints. In analysis, nothing enforces them (a CSV file has no constraints), so you must test them yourself.

Three questions for every foreign key:

1. **Is the parent key unique?** (`customers.customer_id`.)
2. **Does every child row find a parent?** (No orphan `customer_id`.)
3. **Is the relationship the one you expect?** (Each job has exactly one customer; each customer can have many jobs.)

```python run
parent_ok = customers["customer_id"].is_unique
orphans = ~jobs["customer_id"].isin(customers["customer_id"])
print("customers.customer_id unique   :", parent_ok)
print("jobs with an unknown customer  :", int(orphans.sum()))
per_customer = jobs.groupby("customer_id").size()
print("customers with no job at all   :", int((~customers["customer_id"].isin(jobs["customer_id"])).sum()))
print("jobs per customer: min", per_customer.min(), "| median", int(per_customer.median()), "| max", per_customer.max())
```
```text
customers.customer_id unique   : True
jobs with an unknown customer  : 0
customers with no job at all   : 14
jobs per customer: min 1 | median 4 | max 10
```

All three answers come back healthy. In real data, the *orphans* are often the finding: jobs whose customer was deleted, orders from a test account, payments with a typing error in the job id.

### 3.2 Natural and surrogate keys

A **natural key** comes from the real world (an email address, a passport number, `order_number`). A **surrogate key** is an arbitrary ID that the system makes up (`job_id = 5001`). Surrogate keys are stable; natural keys change (people change email addresses), repeat (two shops use the same `order_number`) and arrive in different formats (`" A-17"` and `"a17"`). Whenever you merge data from **two systems**, you are using a natural key, and you should clean it first, exactly as in da.05.

### 3.3 Candidate grain from the data

Sometimes the documentation is missing, and you have to **discover** the grain. The approach: propose a key, test it, and when it fails, find out why. Imagine you receive the payments table with no documentation. What is one row?

```python run
for key in (["payment_id"], ["job_id"], ["job_id", "kind"], ["job_id", "paid_at"]):
    keys = payments.drop_duplicates(subset=key)
    print(f"{str(key):26} distinct = {len(keys):5d} of {len(payments)} rows -> {'unique' if len(keys) == len(payments) else 'repeats'}")
```
```text
['payment_id']             distinct =  3236 of 3236 rows -> unique
['job_id']                 distinct =  2690 of 3236 rows -> repeats
['job_id', 'kind']         distinct =  3236 of 3236 rows -> unique
['job_id', 'paid_at']      distinct =  3236 of 3236 rows -> unique
```

`payment_id` is unique, so it is a key. `["job_id", "kind"]` is also unique here: one deposit and one balance at most per job. That suggests **one payment per job per kind**, which is exactly the business rule we planted. Discovering a composite key like that tells you something about the *business*, and it is a good question to put to the data owner.

> **A key is a claim about the future.** The table is unique *today*. Whether it stays unique depends on a business rule you do not control (can a customer pay a second deposit? can a refund be split?). Write the assumption in your notes; test it again when new data arrives.

### 3.4 Checking relationships between two tables

Before you join, state the expected relationship, and test both sides.

```python run
def relationship(left, right, left_key, right_key):
    """How many right rows match one left row, and the reverse? Returns the relationship as text."""
    l_unique = left[left_key].is_unique
    r_unique = right[right_key].is_unique
    return {(True, True): "one-to-one", (True, False): "one-to-many",
            (False, True): "many-to-one", (False, False): "many-to-many"}[(l_unique, r_unique)]


print("customers -> jobs     :", relationship(customers, jobs, "customer_id", "customer_id"))
print("jobs -> items         :", relationship(jobs, items, "job_id", "job_id"))
print("jobs -> payments      :", relationship(jobs, payments, "job_id", "job_id"))
print("jobs -> refunds       :", relationship(jobs, refunds, "job_id", "job_id"))
print("payments -> refunds   :", relationship(payments, refunds, "job_id", "job_id"))
```
```text
customers -> jobs     : one-to-many
jobs -> items         : one-to-many
jobs -> payments      : one-to-many
jobs -> refunds       : one-to-one
payments -> refunds   : many-to-one
```

`jobs -> items` is **one-to-many**: one job, many lines. `payments -> refunds` through `job_id` is **many-to-one**: a job can have two payments but one refund, so a refund joined to payments is repeated on each of the job's payment rows, and a refund total over that join counts it twice. If the refunds were also repeated per job, the relationship would be **many-to-many**, which multiplies rows in both directions and gets its own treatment in the next section.

## 4. Join fan-out

### 4.1 What fan-out is

You met fan-out in da.04: a join where the right table has several rows for one key makes the left row **multiply**. Here is the theory behind it, with the numbers of our business. **Fan-out** happens when you join along a one-to-many relationship, and then compute a measure that belongs to the "one" side.

```python run
j_it = jobs.merge(items, on="job_id")
print("jobs                 :", len(jobs))
print("jobs joined to items :", len(j_it), "<- one row per line item now")
print("distinct jobs after  :", j_it["job_id"].nunique(), "<- unchanged")
```
```text
jobs                 : 3000
jobs joined to items : 7554 <- one row per line item now
distinct jobs after  : 3000 <- unchanged
```

A left join to a table with several matching rows gives more rows than the left table had. No error, no warning. The *grain* of the result is now "one row per line item", and anything that was at the job grain (`quote_total`, `status`, `created_at`) is repeated. Count the jobs by `len(j_it)` and you get 7,554; count them by `nunique` and you get 3,000.

### 4.2 The three kinds of wrong answer

Fan-out damages different metrics in different ways.

```python run
by_status_wrong = j_it.groupby("status").agg(jobs=("job_id", "size"), quote=("quote_total", "sum"))
by_status_right = jobs.groupby("status").agg(jobs=("job_id", "size"), quote=("quote_total", "sum"))
print("WRONG (after the join)           RIGHT (job grain)")
print(pd.concat([by_status_wrong, by_status_right], axis=1, keys=["after join", "job grain"]).to_string())
```
```text
WRONG (after the join)           RIGHT (job grain)
          after join           job grain         
                jobs     quote      jobs    quote
status                                           
cancelled        602   1902000       240   692000
completed       6755  21264900      2678  7646900
failed           113    319000        50   128600
pending           84    256200        32    90000
```

Counts are inflated (`size` counts the multiplied rows). Sums of job-level values are inflated. **Averages of job-level values are skewed** towards jobs that have many lines, because they are counted more often: a silent bias.

```python run
print("average quote per job, job grain   :", round(jobs["quote_total"].mean()))
print("average quote per job, after join  :", round(j_it["quote_total"].mean()))
```
```text
average quote per job, job grain   : 2852
average quote per job, after join  : 3143
```

The average after the join is higher, since jobs with more lines (more parts, higher total) appear more times and pull the average toward themselves. This is a *weighting* effect: each job is weighted by its number of lines. Sections 5 and 6 return to it.

### 4.3 Three habits that prevent fan-out

**Habit 1: state the grain you want, then reach it.** If the question is about jobs, the final table must have one row per job. If you need a fact from a finer table (items, payments), **aggregate it first** to the job grain, and then join.

```python run
items_per_job = items.groupby("job_id").size().rename("n_lines")
parts = items[items["item"] == "parts"].groupby("job_id")["amount"].sum().rename("parts_total")
paid = payments.groupby("job_id").agg(paid_total=("amount", "sum"), n_payments=("payment_id", "size"))

j = (jobs.merge(items_per_job, on="job_id", how="left", validate="1:1")
         .merge(parts, on="job_id", how="left", validate="1:1")
         .merge(paid, on="job_id", how="left", validate="1:1"))
j["parts_total"] = j["parts_total"].fillna(0)
j["paid_total"] = j["paid_total"].fillna(0)
j["n_payments"] = j["n_payments"].fillna(0).astype(int)
print("rows:", len(j), "(= number of jobs:", len(jobs), ")")
print("total quote still:", f"{j['quote_total'].sum():,}")
print(j[["job_id", "status", "quote_total", "n_lines", "parts_total", "paid_total", "n_payments"]].head(4).to_string(index=False))
```
```text
rows: 3000 (= number of jobs: 3000 )
total quote still: 8,557,500
 job_id    status  quote_total  n_lines  parts_total  paid_total  n_payments
   5001 completed         3800        4     2,400.00    3,800.00           1
   5002 cancelled          800        2         0.00        0.00           0
   5003 completed         2600        2     1,200.00    2,600.00           1
   5004 completed         2500        3     1,700.00    2,500.00           1
```

We aggregated `items` and `payments` to one row per job, **then** joined. The row count stayed at 3,000 and the quote total is untouched. The `validate="1:1"` argument makes pandas raise an error if the right side were not unique: the join checks its own assumption.

**Habit 2: compare counts before and after.** One `len` before, one after, and a message if they differ. You wrote `safe_merge` for this in da.04.

**Habit 3: sum before join, or use distinct.** If you must stay at the finer grain, count with `nunique` and take sums from the table where the column was born.

```python run
check = j_it.groupby("status").agg(jobs_distinct=("job_id", "nunique"))
print(check.join(jobs.groupby("status").size().rename("jobs_truth")).to_string())
```
```text
           jobs_distinct  jobs_truth
status                              
cancelled            240         240
completed           2678        2678
failed                50          50
pending               32          32
```

### 4.4 The many-to-many explosion

When both sides have repeated keys, every pair multiplies. Join the payments to the items on `job_id` (a job with 2 payments and 3 lines gives 6 rows):

```python run
pi = payments.merge(items, on="job_id", suffixes=("_pay", "_line"))
print("payments :", len(payments), "| items :", len(items), "| joined :", len(pi))
print("paid money after the join:", f"{pi['amount_pay'].sum():,}", " vs the truth:", f"{payments['amount'].sum():,}")
```
```text
payments : 3236 | items : 7554 | joined : 8175
paid money after the join: 21,291,630  vs the truth: 7,656,860
```

The joined result has more rows than either input, and the money reported as paid is inflated by about 2.8 times (21.3 million against 7.7 million). **A many-to-many join is almost never what you want**; it is the sign that you joined on a column that is not the key of either side, or that you skipped the aggregation step. If you see a row count that is bigger than either input, stop and look.

### 4.5 Fan-out that hides: the left join

A left join is meant to keep every left row, but with duplicates on the right it keeps them *and adds more*. A common surprise: analysts use a left join "to be safe" and think the row count is protected. It is only protected if the right side is unique on the join key.

```python run
lj = jobs.merge(payments, on="job_id", how="left")
print("left join rows:", len(lj), "| jobs:", len(jobs))
print("jobs counted twice because they have 2 payments:", int(lj.duplicated("job_id").sum()))
print("jobs with no payment (kept, with NaN):", int(lj["payment_id"].isna().sum()))
```
```text
left join rows: 3546 | jobs: 3000
jobs counted twice because they have 2 payments: 546
jobs with no payment (kept, with NaN): 310
```

Jobs with no payment are kept (good); jobs with two payments are doubled (bad). Both effects happen in one join, and the row count only tells you the *net* of the two. This is why section 11 insists on tracing differences in two directions.

### 4.6 The same thing in SQL

SQL has no special safety either. `JOIN` along a one-to-many relationship repeats the left columns. The rule for pandas applies word for word: aggregate to the grain first (in a subquery or a CTE), then join. We build the SQL versions in section 10.


## 5. Counting: rows, values, distinct values

### 5.1 Three counts, three questions

"Count" is not one operation. Take the column `started_at`: some jobs have not started (it is missing). Three different counts exist.

| Question | pandas | SQL | Counts |
|---|---|---|---|
| How many rows? | `len(df)`, `size()` | `COUNT(*)` | every row |
| How many rows have a value? | `count()` | `COUNT(col)` | rows where the column is **not missing** |
| How many different values? | `nunique()` | `COUNT(DISTINCT col)` | distinct non-missing values |

```python run
print("rows (jobs)                     :", len(jobs))
print("count of started_at             :", jobs["started_at"].count(), " <- jobs that have started")
print("count of completed_at           :", jobs["completed_at"].count())
print("distinct customers with a job   :", jobs["customer_id"].nunique(), "of", len(customers))
print("distinct statuses               :", jobs["status"].nunique())
```
```text
rows (jobs)                     : 3000
count of started_at             : 2728  <- jobs that have started
count of completed_at           : 2678
distinct customers with a job   : 786 of 800
distinct statuses               : 4
```

`count` on a date column quietly answers "how many jobs have started", which is a *metric*, not a technicality. Many dashboards compute "jobs completed" as `COUNT(completed_at)`; that is correct only if a completed job always has a `completed_at`, and only if no other status has one. You will test that in section 9.

### 5.2 Distinct counts do not add up

A very common mistake: summing distinct counts. "How many different customers booked a job each week?" Add the weekly numbers and you count a customer who booked in three weeks three times.

```python run
f = jobs[feb(jobs["created_at"])].copy()
f["week"] = f["created_at"].dt.to_period("W-SUN").astype(str)
weekly = f.groupby("week")["customer_id"].nunique()
print(weekly.to_string())
print("\nsum of the weekly distinct counts      :", int(weekly.sum()))
print("distinct customers in the whole month  :", f["customer_id"].nunique())
```
```text
week
2025-01-27/2025-02-02     76
2025-02-03/2025-02-09    207
2025-02-10/2025-02-16    183
2025-02-17/2025-02-23    197
2025-02-24/2025-03-02    133

sum of the weekly distinct counts      : 796
distinct customers in the whole month  : 549
```

The weekly numbers sum to more than the monthly distinct count, because many customers appear in several weeks. **Distinct counts are not additive across groups.** If a dashboard shows "unique customers" for each week and a total, the total must be computed from the rows again, not from the weekly figures. The same applies to "unique visitors per day" against "unique visitors per month", and to any cut by region, product or channel.

Compare the rules.

| Measure | Additive across groups? | Why |
|---|---|---|
| Row count, sum of an amount | yes, if the groups do not overlap | each row is in exactly one group |
| Distinct count | **no** | the same value can be in several groups |
| Average, rate, ratio | **no** | needs the numerator and denominator (section 6) |
| Maximum, minimum | only with `max`/`min` of the parts | not a sum |

Two ways to handle it: compute each level from the raw rows with its own `nunique`, or store the *sets* (not the counts) so you can union them later. For reports, the first way is simpler and safer.

> **Predict the output.** Customers can book in several cities in this synthetic data (the `city` column is on the customer, so no). Instead think about *segment*: each customer has exactly one segment. If you sum the distinct customers per segment in February, will the sum equal the overall distinct count?

<details><summary>Answer</summary>

```python run
per_segment = f.merge(customers[["customer_id", "segment"]], on="customer_id", validate="m:1").groupby("segment")["customer_id"].nunique()
print(per_segment.to_dict(), "sum:", int(per_segment.sum()), "| overall:", f["customer_id"].nunique())
```
```text
{'business': 129, 'home': 420} sum: 549 | overall: 549
```

Yes, they are equal here, because a customer belongs to exactly one segment, so the groups do not overlap. The rule "distinct counts are not additive" is really "not additive when a value can belong to more than one group". Check whether the groups overlap before you add. Weeks overlap (a customer returns), segments do not.

</details>

### 5.3 Denominators

Every percentage has two counts, and the second one is where people disagree. "What share of customers booked at least once in February?" depends on the denominator: all 800 customers ever, customers that exist at the start of February, or customers who were active in the last 90 days?

```python run
active = f["customer_id"].nunique()
print("customers who booked in February :", active)
print("... as a share of all 800        :", round(active / len(customers) * 100, 1), "%")
print("... as a share of those who ever booked:", round(active / jobs["customer_id"].nunique() * 100, 1), "%")
```
```text
customers who booked in February : 549
... as a share of all 800        : 68.6 %
... as a share of those who ever booked: 69.8 %
```

Two honest denominators, two honest percentages. The **name** of the metric must say which one. This is the heart of section 7.

## 6. Averages: simple, weighted, and Simpson's paradox

### 6.1 The average of averages

Suppose you have the average quote for each city and you want the overall average. The natural move is to average the four city averages. It is wrong whenever the cities have different numbers of jobs.

```python run
by_city = jobs.merge(customers[["customer_id", "city"]], on="customer_id", validate="m:1").groupby("city")["quote_total"].agg(["count", "mean"])
by_city["mean"] = by_city["mean"].round(0)
print(by_city.to_string())
print()
print("average of the city averages  :", round(by_city["mean"].mean()))
print("weighted by the job counts    :", round((by_city["mean"] * by_city["count"]).sum() / by_city["count"].sum()))
print("true average over all jobs    :", round(jobs["quote_total"].mean()))
```
```text
        count     mean
city                  
Delhi     998 2,823.00
Jaipur    253 2,814.00
Mumbai    946 2,882.00
Pune      803 2,866.00

average of the city averages  : 2846
weighted by the job counts    : 2852
true average over all jobs    : 2852
```

The weighted average (each city's mean times its number of jobs, divided by all jobs) equals the true average. The simple average of the averages treats small Jaipur as important as large Delhi. The difference is small here because the cities have similar averages, but the **method** is wrong, and with a larger spread it would give a large error.

The rule, in general:

> **Never average rates or averages. Add the numerators, add the denominators, and divide once.**

An average is `sum / count`. To combine groups you need the sums and counts, not the averages. This is true for the mean, for rates ("completion rate"), for ratios ("revenue per job") and for percentages.

### 6.2 Which average? The unit of analysis

Even for one table there are several correct averages, depending on **what is averaged over**.

```python run
jc = jobs.merge(customers[["customer_id", "city"]], on="customer_id", validate="m:1")
per_job = jc["quote_total"].mean()
per_customer = jc.groupby("customer_id")["quote_total"].sum().mean()
per_customer_avg = jc.groupby("customer_id")["quote_total"].mean().mean()
print(f"average quote per JOB                         : {per_job:8,.0f}")
print(f"average total spend per CUSTOMER              : {per_customer:8,.0f}")
print(f"average of each customer's average quote      : {per_customer_avg:8,.0f}")
```
```text
average quote per JOB                         :    2,852
average total spend per CUSTOMER              :   10,887
average of each customer's average quote      :    2,863
```

Three honest numbers for "the average amount". They answer three questions: how big is a typical job, how much does a typical customer spend, and what is the typical customer's typical job. A customer with ten small jobs counts ten times in the first and once in the others. **The unit of the average (job, customer, day) must be in the metric's name**: "average quote per job".

### 6.3 Weighted and unweighted, in pandas

`np.average(values, weights=...)` does the weighted mean in one call. A weighted mean is also the right way to combine group results when you only have the group results.

```python run
lag = (jobs["started_at"] - jobs["created_at"]).dt.total_seconds() / 3600
jl = jobs.assign(lag_h=lag).merge(customers[["customer_id", "city"]], on="customer_id", validate="m:1")
grp = jl.groupby("city")["lag_h"].agg(["count", "mean"])
print(grp.round(1).to_string())
print("simple mean of the 4 city means:", round(grp["mean"].mean(), 2))
print("weighted by non-missing counts :", round(np.average(grp["mean"], weights=grp["count"]), 2))
print("direct mean over all rows      :", round(jl["lag_h"].mean(), 2))
```
```text
        count  mean
city               
Delhi     903 76.50
Jaipur    236 82.10
Mumbai    847 77.10
Pune      742 77.20
simple mean of the 4 city means: 78.22
weighted by non-missing counts : 77.36
direct mean over all rows      : 77.36
```

Note the weights are the number of **non-missing** values (`count`), not `size`: jobs that never started have no lag, so they must not carry weight. Weighted by `size` would be wrong by a small amount here, and by a large amount if one city had many cancelled jobs.

### 6.4 Simpson's paradox

A trend that appears in every group can reverse when the groups are combined. This is **Simpson's paradox**, and it is not a curiosity: it appears in real data whenever groups differ in size *and* in difficulty. Here is a simplified, hand-made example about two technician teams. A team's success rate is measured on two kinds of job: easy and hard.

```python run
teams = pd.DataFrame({
    "team": ["A", "A", "B", "B"],
    "kind": ["easy", "hard", "easy", "hard"],
    "jobs": [87, 263, 270, 80],
    "done": [81, 192, 234, 55],
})
teams["rate_%"] = (teams["done"] / teams["jobs"] * 100).round(1)
print(teams.to_string(index=False))
tot = teams.groupby("team")[["jobs", "done"]].sum()
tot["rate_%"] = (tot["done"] / tot["jobs"] * 100).round(1)
print()
print(tot.to_string())
```
```text
team kind  jobs  done  rate_%
   A easy    87    81   93.10
   A hard   263   192   73.00
   B easy   270   234   86.70
   B hard    80    55   68.80

      jobs  done  rate_%
team                    
A      350   273   78.00
B      350   289   82.60
```

Team A has the better success rate for the easy jobs (93.1 against 86.7) **and** for the hard jobs (73.0 against 68.8). Yet Team B has the better rate overall (82.6 against 78.0). Both statements are arithmetic facts. The reason: Team A was given mostly hard jobs (263 of 350), Team B mostly easy ones (270 of 350). The overall rate is a weighted average of the two rates, with different weights for each team.

Which comparison should you trust? Not the overall one. Compare teams on the same mix of jobs, i.e., **within** a kind of job, or re-weight both teams to a common mix. If you only report the overall rate, you reward the team for choosing easy work. The way out is always the same: ask what *else* differs between the groups (here, the difficulty), and break the metric down by it.

> **Try it.** Compute the overall rate for each team if both teams had exactly the same job mix: 50 percent easy, 50 percent hard. Who wins now?

<details><summary>Answer</summary>

```python run
rates = teams.pivot(index="team", columns="kind", values="done") / teams.pivot(index="team", columns="kind", values="jobs")
standardised = rates["easy"] * .5 + rates["hard"] * .5
print((standardised * 100).round(1).to_string())
```
```text
team
A   83.10
B   77.70
```

Team A: 83.1 percent, Team B: 77.7 percent. With the same mix, A wins, which agrees with the two comparisons *within* each kind. This technique is called **standardisation**: choose a fixed set of weights, apply it to every group, and compare fairly. It is how hospitals, schools and sales teams are compared without being punished for taking on the hardest cases.

</details>

## 7. Metric definitions

### 7.1 A metric is a promise

A metric is not a column name. It is a **promise**: "whenever you read this number, it was computed this way." A promise needs to be written down precisely enough that two people, working apart, compute the same value. The list of ingredients is always the same.

| Ingredient | The question it answers | Example for "completed jobs in February" |
|---|---|---|
| **Name** | what do we call it, in one phrase? | `completed_jobs` |
| **Business question** | why does anyone want it? | how much work did we finish this month? |
| **Grain** | what is counted (one row = ?) | a job |
| **Numerator** | what goes in the top, exactly | jobs with `status = 'completed'` |
| **Denominator** | what goes in the bottom (for a rate) | not applicable (a count) |
| **Date basis** | which timestamp places the row in a month | `completed_at` |
| **Time zone** | where is "the month" | IST (UTC+05:30) |
| **Inclusions / exclusions** | what is in, what is out | exclude test customers; include refunded jobs |
| **Unit and currency** | what unit | jobs |
| **Owner and version** | who answers questions; when did it change | finance, v2 |

If any line is left out, two people will fill it in differently. That is how three analysts produced three Februaries in section 1.

### 7.2 One name, four definitions

"Completion rate" sounds precise. It is not. Here are four definitions that real teams use for it, all with a straight face.

```python run
def in_period(s, start, end):
    """A half-open interval: start included, end excluded (section 8.2)."""
    return (s >= start) & (s < end)


def completion_rates(d, start, end):
    created = in_period(d["created_at"], start, end)
    done = d["status"].eq("completed")
    return {
        "1  completed / created": (done & created).sum() / created.sum(),
        "2  completed / (created - pending)": (done & created).sum() / (created & ~d["status"].eq("pending")).sum(),
        "3  completed / started": (done & created).sum() / (created & d["started_at"].notna()).sum(),
        "4  completed_in_period / created_in_period": in_period(d["completed_at"], start, end).sum() / created.sum(),
    }


r_feb = completion_rates(jobs, pd.Timestamp("2025-02-01"), pd.Timestamp("2025-03-01"))
r_mar = completion_rates(jobs, pd.Timestamp("2025-03-01"), pd.Timestamp("2025-04-01"))
print(f"{'definition':45} {'February':>9} {'March':>9}")
for k in r_feb:
    print(f"{k:45} {r_feb[k] * 100:8.2f}% {r_mar[k] * 100:8.2f}%")
```
```text
definition                                     February     March
1  completed / created                           89.16%    87.68%
2  completed / (created - pending)               89.16%    90.38%
3  completed / started                           98.40%    98.22%
4  completed_in_period / created_in_period       90.17%    90.20%
```

Four numbers for the one phrase "completion rate". In February, definitions 1 and 2 agree (89.16 percent), because every job created in February has long since left the pending state. In March they separate, because 32 jobs are still pending and definition 1 counts them as not completed. Definition 3 is the highest in both months (98.4 percent in February): it hides every cancellation, since a cancelled job never started. Definition 4 divides jobs of one group by jobs of another group: the numerator contains jobs created in January, and the denominator does not contain them, so the ratio is not a share of anything. A rate whose numerator is not a subset of its denominator is a warning sign.

The **subset rule**: for a rate (a share), every row in the numerator must also be in the denominator. If you cannot say so, the metric is not a rate, it is just a quotient.

### 7.3 Writing the definition as code

A definition on a wiki page can drift from the code. A cleaner approach keeps **both in one place**: a small object that holds the text and the function that computes the number.

```python run
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Metric:
    name: str
    question: str
    grain: str
    numerator: str
    denominator: str
    date_basis: str
    exclusions: str
    compute: Callable                      # compute(jobs, start, end) -> number

    def describe(self):
        return (f"{self.name}\n  question   : {self.question}\n  grain      : {self.grain}\n"
                f"  numerator  : {self.numerator}\n  denominator: {self.denominator}\n"
                f"  date basis : {self.date_basis}\n  exclusions : {self.exclusions}")


METRICS = {}


def register(m):
    METRICS[m.name] = m
    return m


register(Metric(
    name="jobs_created", question="how much demand arrived?", grain="job",
    numerator="jobs", denominator="-", date_basis="created_at (UTC)", exclusions="none",
    compute=lambda j, s, e: int(in_period(j["created_at"], s, e).sum())))

register(Metric(
    name="jobs_completed", question="how much work was finished?", grain="job",
    numerator="jobs with status completed", denominator="-", date_basis="completed_at (UTC)", exclusions="none",
    compute=lambda j, s, e: int((j["status"].eq("completed") & in_period(j["completed_at"], s, e)).sum())))

register(Metric(
    name="completion_rate_created_cohort", question="of the demand that arrived, how much was finished?", grain="job",
    numerator="jobs created in the period with status completed",
    denominator="jobs created in the period, excluding status pending",
    date_basis="created_at (UTC)", exclusions="pending jobs are not yet decided",
    compute=lambda j, s, e: (lambda c: (c["status"].eq("completed").sum() / (~c["status"].eq("pending")).sum()))(j[in_period(j["created_at"], s, e)])))

for m in METRICS.values():
    print(m.describe(), "\n")
```
```text
jobs_created
  question   : how much demand arrived?
  grain      : job
  numerator  : jobs
  denominator: -
  date basis : created_at (UTC)
  exclusions : none 

jobs_completed
  question   : how much work was finished?
  grain      : job
  numerator  : jobs with status completed
  denominator: -
  date basis : completed_at (UTC)
  exclusions : none 

completion_rate_created_cohort
  question   : of the demand that arrived, how much was finished?
  grain      : job
  numerator  : jobs created in the period with status completed
  denominator: jobs created in the period, excluding status pending
  date basis : created_at (UTC)
  exclusions : pending jobs are not yet decided 
```

Each metric now has its description next to its code. The `compute` function takes the table and the period, so the **same code** is used for February, March, and any other month. Names are precise: `jobs_completed` and `jobs_created` cannot be confused; `completion_rate_created_cohort` says it is a cohort (jobs grouped by when they were created). Let us compute them.

```python run
S_, E_ = pd.Timestamp("2025-02-01"), pd.Timestamp("2025-03-01")
for name, m in METRICS.items():
    v = m.compute(jobs, S_, E_)
    print(f"{name:34} {v if isinstance(v, int) else round(float(v) * 100, 2)}{'' if isinstance(v, int) else ' %'}")
```
```text
jobs_created                       895
jobs_completed                     807
completion_rate_created_cohort     89.16 %
```

This is the principle behind a **metrics layer** or a **semantic layer** in analytics tools: define each metric once, in one place, with its text, and make every dashboard read from it. You do not need a tool to start. A dictionary like `METRICS` kept in the repository already prevents most disagreements.

### 7.4 Metric hygiene

A few rules that save arguments.

1. **One metric, one name.** If two definitions are needed, give them two names.
2. **Put the unit and the date basis in the name** when there is a choice: `revenue_by_paid_date`, `jobs_by_created_date`.
3. **A rate shows its numerator and denominator.** Show "798 of 895 (89.2 percent)", not just "89.2 percent". The reader sees how many jobs stand behind it.
4. **A change in a definition is a version.** If finance moves from `created_at` to `completed_at`, the old and new series are different metrics. Mark the date and do not splice them.
5. **Write the exclusions as rules, not as habits.** "We never count test accounts" must be a filter in the code, not a thing that Priya remembers to do.

## 8. Dates: the basis of a metric

### 8.1 Which timestamp?

One job has many dates. A month is a *bucket*, and the date basis decides which bucket a job falls into.

```python run
j1 = jobs.loc[jobs["status"] == "completed"].iloc[0]
print(j1[["job_id", "created_at", "started_at", "completed_at"]].to_string())
paid = payments[payments["job_id"] == j1["job_id"]][["kind", "paid_at", "amount"]]
print(paid.to_string(index=False))
```
```text
job_id                                   5001
created_at                2025-01-19 23:55:00
started_at      2025-02-02 21:58:11.571412201
completed_at    2025-02-03 01:46:38.548171749
kind                       paid_at  amount
full 2025-02-04 22:57:42.607955092    3800
```

A single job can be created in one month, started in the next, completed in the same month as the start, and paid in the one after. The date basis is a *business decision*: **demand** is counted at `created_at`, **work done** at `started_at` or `completed_at`, **cash** at `paid_at`, **revenue recognised** by the accounting rule. None is wrong. Each answers a different question, and each one belongs under its own name.

### 8.2 Half-open intervals

Always define a period as **start included, end excluded**: `start <= t < end`. February is `>= 2025-02-01` and `< 2025-03-01`. Writing `<= 2025-02-28` is a classic bug, because `2025-02-28 15:30` is greater than `2025-02-28 00:00`, so the last day silently loses all its afternoon.

```python run
bad_end = (jobs["created_at"] >= "2025-02-01") & (jobs["created_at"] <= "2025-02-28")
good_end = feb(jobs["created_at"])
print("February with '<= 2025-02-28' :", int(bad_end.sum()))
print("February, half-open interval  :", int(good_end.sum()))
print("jobs lost on the last day     :", int(good_end.sum() - bad_end.sum()))
```
```text
February with '<= 2025-02-28' : 873
February, half-open interval  : 895
jobs lost on the last day     : 22
```

The half-open interval also has the nice property that consecutive periods join with no gap and no overlap: the end of February is the start of March.

### 8.3 Time zones

All our timestamps are UTC, but the business lives in IST, which is 5 hours 30 minutes ahead. A job created at 20:00 UTC on 31 January is, for the customer, 01:30 on 1 February. If you cut the month on UTC and the manager cuts it on IST, their Februaries differ.

```python run
IST = pd.Timedelta(hours=5, minutes=30)
created_ist = jobs["created_at"] + IST                      # local time as a plain shift
feb_utc = feb(jobs["created_at"])
feb_ist = feb(created_ist)
print("February by UTC dates:", int(feb_utc.sum()))
print("February by IST dates:", int(feb_ist.sum()))
moved_in = feb_ist & ~feb_utc
moved_out = feb_utc & ~feb_ist
print("jobs that are February only in IST:", int(moved_in.sum()), " (created 18:30-24:00 UTC on 31 January)")
print("jobs that are February only in UTC:", int(moved_out.sum()), " (created 18:30-24:00 UTC on 28 February)")
```
```text
February by UTC dates: 895
February by IST dates: 895
jobs that are February only in IST: 3  (created 18:30-24:00 UTC on 31 January)
jobs that are February only in UTC: 3  (created 18:30-24:00 UTC on 28 February)
```

The two totals are the same (895), but only by coincidence: 3 jobs entered February and 3 left it. The border moves by 5.5 hours, so some jobs change month, and the *set* of jobs differs even when its size does not. The set is what matters when someone says "send me the list", and for a quarter or a year the sizes would not match either. Pandas also offers `tz_localize("UTC").dt.tz_convert("Asia/Kolkata")`, which handles daylight saving time as well; for IST, a fixed shift is exact, because India does not use daylight saving time. The lesson is independent of the tool: **state the time zone in the definition of every date metric.**

### 8.4 Immature cohorts

Look at the completion rate of jobs by the week they were created.

```python run
w = jobs.assign(week=jobs["created_at"].dt.to_period("W-SUN").dt.start_time)
wk = w.groupby("week").agg(created=("job_id", "size"),
                           completed=("status", lambda s: (s == "completed").sum()),
                           pending=("status", lambda s: (s == "pending").sum()))
wk["completed_%"] = (wk["completed"] / wk["created"] * 100).round(1)
print(wk.tail(6).to_string())
```
```text
            created  completed  pending  completed_%
week                                                
2025-02-24      232        209        0        90.10
2025-03-03      261        241        0        92.30
2025-03-10      237        219        0        92.40
2025-03-17      222        195        3        87.80
2025-03-24      234        178       25        76.10
2025-03-31       28         24        4        85.70
```

The last weeks show a lower completion rate, only because many of their jobs are still **pending**: the data were extracted on 5 April and the work has not happened yet. The newest cohorts have not had time to complete. This is called **right-censoring** or an **immature cohort**. The week of 24 March shows 76 percent against 90 to 92 percent in the weeks before, and concluding that "quality fell" would be wrong; the figure is still moving. Three safe answers: compare only cohorts old enough (for example, jobs created at least 14 days before the extraction), report the pending count beside the rate, or use a rate that excludes pending jobs from the denominator and say so (definition 2 in section 7.2).

> **Predict the output.** If you run the same query a week later, will the completion rate for jobs created in the last week of March go up or down? And the rate for January?

<details><summary>Answer</summary>

The rate for the last week of March will go **up**, since some of its pending jobs will have been completed (cancellations among them will pull a little the other way). The rate for January will hardly change, because almost nothing is pending there. This is why a dashboard that shows only the latest period is often misleading, and why many teams freeze reports ("as of the 5th of the next month") for the official numbers.

</details>

### 8.5 Partial periods

April holds only 5 days of data. A monthly table that shows "April: 62 jobs started" next to "March: 973" invites a false conclusion. Either drop the incomplete period, label it "(partial)", or compare like with like (the first 5 days of each month). The label costs nothing; the wrong conclusion can cost a decision.

## 9. Status and lifecycle

### 9.1 Status is a state

A job moves through a lifecycle: it is created, then pending, then it ends in `completed`, `cancelled` or `failed`. The `status` column holds the **current** state, as of the extraction. It does not tell you what the state was last month.

A well-built status column is a **partition**: every row has exactly one value, and the values together cover everything.

```python run
counts = jobs["status"].value_counts()
print(counts.to_string())
print("sum of the statuses:", int(counts.sum()), "| jobs:", len(jobs), "| missing status:", int(jobs["status"].isna().sum()))
```
```text
status
completed    2678
cancelled     240
failed         50
pending        32
sum of the statuses: 3000 | jobs: 3000 | missing status: 0
```

The counts add up to the number of jobs. Because the statuses are mutually exclusive and exhaustive, "total = completed + cancelled + failed + pending" holds exactly **at the job grain with a single date basis**. When it fails, someone changed the basis or the filter.

### 9.2 Does the status agree with the timestamps?

The status and the timestamps describe the same facts, so they can contradict each other. A job with status `completed` but no `completed_at` is a data defect, and any metric that counts through the timestamp will disagree with one that counts through the status. Check with a table of "which timestamps exist for each status".

```python run
exists = jobs[["started_at", "completed_at", "cancelled_at"]].notna()
exists["status"] = jobs["status"]
print(exists.groupby("status").mean().mul(100).round(0).astype(int).astype(str).add(" %").to_string())
```
```text
          started_at completed_at cancelled_at
status                                        
cancelled        0 %          0 %        100 %
completed      100 %        100 %          0 %
failed          98 %          0 %          0 %
pending          3 %          0 %          0 %
```

Read it: 100 % of `completed` jobs have `started_at` and `completed_at`, and none have `cancelled_at`. `cancelled` jobs have `cancelled_at` and never started. `pending` jobs have no `completed_at`, and (almost) no `started_at`. `failed` jobs (98 percent of them had started) have neither a completion nor a cancellation timestamp: a **gap** in the data, since *when* a job failed is unknown. Any metric by "failed date" is impossible with this table. That is worth knowing before a manager asks for it.

We wrap the checks into a function that lists contradictions.

```python run
def lifecycle_problems(j):
    """Rows whose status contradicts their timestamps. Returns a dict of problem name -> number of rows."""
    return {
        "completed without completed_at": int((j["status"].eq("completed") & j["completed_at"].isna()).sum()),
        "completed_at on a non-completed job": int((j["status"].ne("completed") & j["completed_at"].notna()).sum()),
        "cancelled without cancelled_at": int((j["status"].eq("cancelled") & j["cancelled_at"].isna()).sum()),
        "cancelled but started": int((j["status"].eq("cancelled") & j["started_at"].notna()).sum()),
        "completed before it started": int((j["completed_at"] < j["started_at"]).sum()),
        "started before it was created": int((j["started_at"] < j["created_at"]).sum()),
    }


print("real table  :", lifecycle_problems(jobs))
broken = jobs.copy()
broken.loc[broken.index[:3], "completed_at"] = pd.NaT           # three completed jobs lose their timestamp
broken.loc[broken["status"].eq("pending").idxmax(), "completed_at"] = pd.Timestamp("2025-03-01")   # a pending job with a completion
print("damaged copy:", lifecycle_problems(broken))
```
```text
real table  : {'completed without completed_at': 0, 'completed_at on a non-completed job': 0, 'cancelled without cancelled_at': 0, 'cancelled but started': 0, 'completed before it started': 0, 'started before it was created': 0}
damaged copy: {'completed without completed_at': 2, 'completed_at on a non-completed job': 1, 'cancelled without cancelled_at': 0, 'cancelled but started': 0, 'completed before it started': 1, 'started before it was created': 0}
```

All zero on the real table. On a damaged copy, the function pinpoints the problems. Run this kind of check **before** you compute any status-based metric, and again whenever the source changes. In real systems these contradictions are common: a job is completed in the app, but the timestamp is written by a different process that failed that night.

### 9.3 Snapshot against history

The `status` column is a **snapshot**: a picture of the present. A question such as "how many jobs were pending at the end of February?" needs the status *then*. That needs a status history (an event table with a row for every change), or you must rebuild the history from timestamps. We can rebuild it for completed and cancelled jobs, because they have timestamps.

```python run
def pending_on(j, when):
    """Jobs created by `when` and not yet completed or cancelled at `when`. 'failed' has no timestamp, so it is unknowable."""
    created = j["created_at"] <= when
    done = j["completed_at"].notna() & (j["completed_at"] <= when)
    cancelled = j["cancelled_at"].notna() & (j["cancelled_at"] <= when)
    return created & ~done & ~cancelled


for d in ["2025-01-31", "2025-02-28", "2025-03-31"]:
    p = pending_on(jobs, pd.Timestamp(d) + pd.Timedelta(hours=23, minutes=59))
    failed_among = int((p & jobs["status"].eq("failed")).sum())
    print(f"open at the end of {d}: {int(p.sum()):4d} jobs | of these, currently 'failed' (state then unknown): {failed_among}")
```
```text
open at the end of 2025-01-31:  118 jobs | of these, currently 'failed' (state then unknown): 20
open at the end of 2025-02-28:  123 jobs | of these, currently 'failed' (state then unknown): 33
open at the end of 2025-03-31:  144 jobs | of these, currently 'failed' (state then unknown): 50
```

A job that failed in March was "open" in February, and our rebuild cannot tell when it failed: it counts failed jobs as open forever. The numbers are therefore an **upper bound**, and we say so. A better source is an event table. If you control the system, keep one: **snapshots lose history, event logs keep it.**

### 9.4 What status means for each metric

| Metric | Which statuses count | Typical mistake |
|---|---|---|
| Demand (jobs created) | all of them | leaving out cancelled jobs |
| Work done | `completed` only | counting `pending` that has started |
| Revenue | `completed` (less refunds) | counting the quote of cancelled jobs |
| Cancellation rate | `cancelled` over all created | dividing by completed jobs only |
| Backlog | `pending` | forgetting jobs that are old and stuck |

The statuses are a tool for building the numerator and the denominator. Decide the status rule first; then the code is trivial.


## 10. The same questions in SQL

Most companies keep their data in a database, and many dashboards are SQL queries. Everything above applies unchanged, and a good analyst can run a question both ways, in pandas and in SQL, and compare. We use `sqlite3` from the standard library. The tables go in an in-memory database; timestamps are stored as text in the ISO format `YYYY-MM-DD HH:MM:SS`, which sorts correctly and which SQLite's date functions understand.

```python run
con = sqlite3.connect(":memory:")
for name, t in [("customers", customers), ("jobs", jobs), ("items", items), ("payments", payments), ("refunds", refunds)]:
    t = t.copy()
    for c in t.columns:
        if pd.api.types.is_datetime64_any_dtype(t[c]):
            t[c] = t[c].dt.strftime("%Y-%m-%d %H:%M:%S")
    t.to_sql(name, con, index=False)


def q(sql, params=()):
    """Run a query and return a DataFrame."""
    return pd.read_sql_query(sql, con, params=params)


print(q("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")["name"].tolist())
print(q("SELECT job_id, created_at, started_at, status FROM jobs LIMIT 3").to_string(index=False))
```
```text
['customers', 'items', 'jobs', 'payments', 'refunds']
 job_id          created_at          started_at    status
   5001 2025-01-19 23:55:00 2025-02-02 21:58:11 completed
   5002 2025-03-07 21:39:00                 NaN cancelled
   5003 2025-03-31 19:20:00 2025-04-01 07:49:16 completed
```

### 10.1 The three counts

```python run
print(q("""
SELECT COUNT(*)                AS rows_,
       COUNT(started_at)       AS started,
       COUNT(DISTINCT customer_id) AS customers
FROM jobs
""").to_string(index=False))
```
```text
 rows_  started  customers
  3000     2728        786
```

The same three numbers as section 5 (3,000, 2,728, 786): `COUNT(*)` counts rows, `COUNT(col)` counts non-null values, `COUNT(DISTINCT col)` counts different values.

### 10.2 One table, three Februaries

```python run
print(q("""
SELECT 'created'   AS basis, COUNT(*) AS jobs FROM jobs WHERE created_at   >= '2025-02-01' AND created_at   < '2025-03-01'
UNION ALL
SELECT 'started',            COUNT(*)         FROM jobs WHERE started_at   >= '2025-02-01' AND started_at   < '2025-03-01'
UNION ALL
SELECT 'completed',          COUNT(*)         FROM jobs WHERE completed_at >= '2025-02-01' AND completed_at < '2025-03-01'
""").to_string(index=False))
```
```text
    basis  jobs
  created   895
  started   820
completed   807
```

Same 895, 820 and 807. Note how SQL treats the missing timestamps: `started_at >= '2025-02-01'` is `NULL` (unknown) for a job that has not started, and a `WHERE` keeps only rows where the condition is *true*, so those jobs drop out of the count silently. That is the same effect as the pandas comparison on `NaT`, which gives `False`. **In both worlds, a filter on a nullable column removes the rows where it is null.**

### 10.3 Fan-out in SQL

```python run
wrong = q("SELECT SUM(j.quote_total) AS total FROM jobs j JOIN items i ON i.job_id = j.job_id")["total"][0]
right = q("SELECT SUM(quote_total) AS total FROM jobs")["total"][0]
fixed = q("""
WITH per_job AS (SELECT job_id, SUM(amount) AS lines_total FROM items GROUP BY job_id)
SELECT SUM(j.quote_total) AS total FROM jobs j JOIN per_job p ON p.job_id = j.job_id
""")["total"][0]
print(f"join to items (fan-out) : {wrong:>12,}")
print(f"jobs only               : {right:>12,}")
print(f"aggregate first, join   : {fixed:>12,}")
```
```text
join to items (fan-out) :   23,742,100
jobs only               :    8,557,500
aggregate first, join   :    8,557,500
```

The first query reproduces the 2.77 times inflation of section 2.2. The third query is the fix: aggregate the many side to the grain of the one side **in a CTE** (`WITH ... AS`), then join. The pattern is always: *aggregate, then join.*

The left-join version of the payments problem:

```python run
print(q("""
SELECT COUNT(*) AS rows_after_join,
       COUNT(DISTINCT j.job_id) AS distinct_jobs,
       SUM(CASE WHEN p.payment_id IS NULL THEN 1 ELSE 0 END) AS jobs_without_payment
FROM jobs j LEFT JOIN payments p ON p.job_id = j.job_id
""").to_string(index=False))
```
```text
 rows_after_join  distinct_jobs  jobs_without_payment
            3546           3000                   310
```

3,546 rows for 3,000 jobs, as in pandas. `COUNT(DISTINCT j.job_id)` recovers the right count, but any `SUM` of a job-level value would still be wrong.

### 10.4 Weighted averages and NULL

`AVG(x)` is `SUM(x) / COUNT(x)`: it skips `NULL`. `AVG` of a column of per-group averages is the average of averages, which is wrong for the same reason as in pandas.

```python run
print(q("""
WITH city_avg AS (
  SELECT c.city, COUNT(*) AS n, AVG(j.quote_total) AS avg_quote
  FROM jobs j JOIN customers c ON c.customer_id = j.customer_id GROUP BY c.city)
SELECT ROUND(AVG(avg_quote), 1)                          AS average_of_averages,
       ROUND(SUM(avg_quote * n) * 1.0 / SUM(n), 1)       AS weighted,
       (SELECT ROUND(AVG(quote_total), 1) FROM jobs)     AS direct
FROM city_avg
""").to_string(index=False))
```
```text
 average_of_averages  weighted   direct
            2,846.40  2,852.50 2,852.50
```

A second NULL trap: `status <> 'completed'` is unknown when `status` is `NULL`, so the row is dropped. Our `status` has no nulls, but a real table might. Use `status IS NOT 'completed'` in SQLite (or `IS DISTINCT FROM` in PostgreSQL) when you mean "everything else, including unknown".

### 10.5 Time zones in SQL

```python run
print(q("""
SELECT 'UTC' AS basis, COUNT(*) AS jobs FROM jobs WHERE created_at >= '2025-02-01' AND created_at < '2025-03-01'
UNION ALL
SELECT 'IST', COUNT(*) FROM jobs
WHERE datetime(created_at, '+330 minutes') >= '2025-02-01' AND datetime(created_at, '+330 minutes') < '2025-03-01'
""").to_string(index=False))
```
```text
basis  jobs
  UTC   895
  IST   895
```

`datetime(x, '+330 minutes')` shifts by 5 hours 30 minutes, as `jobs["created_at"] + IST` did. Same totals, same coincidence. In PostgreSQL you would write `created_at AT TIME ZONE 'Asia/Kolkata'`; the idea is the same: **convert first, then truncate to the day or month.**

### 10.6 Two engines, one answer

A strong habit: compute the metric in pandas and in SQL, and compare. If they disagree, one has a bug in its logic, and the disagreement shows where to look.

```python run
def both_ways(name, pandas_value, sql):
    sql_value = q(sql).iloc[0, 0]
    ok = abs(float(pandas_value) - float(sql_value)) < 1e-9
    print(f"{name:34} pandas={pandas_value:>12,.2f}  sql={float(sql_value):>12,.2f}  {'MATCH' if ok else 'MISMATCH'}")


both_ways("jobs created in Feb", feb(jobs["created_at"]).sum(),
          "SELECT COUNT(*) FROM jobs WHERE created_at >= '2025-02-01' AND created_at < '2025-03-01'")
both_ways("completed quote value", jobs.loc[jobs["status"] == "completed", "quote_total"].sum(),
          "SELECT SUM(quote_total) FROM jobs WHERE status = 'completed'")
both_ways("paid money", payments["amount"].sum(), "SELECT SUM(amount) FROM payments")
both_ways("net revenue (paid - refunds)", payments["amount"].sum() - refunds["amount"].sum(),
          "SELECT (SELECT SUM(amount) FROM payments) - (SELECT SUM(amount) FROM refunds)")
```
```text
jobs created in Feb                pandas=      895.00  sql=      895.00  MATCH
completed quote value              pandas=7,646,900.00  sql=7,646,900.00  MATCH
paid money                         pandas=7,656,860.00  sql=7,656,860.00  MATCH
net revenue (paid - refunds)       pandas=7,434,510.00  sql=7,434,510.00  MATCH
```

## 11. Reconciliation: from a total to the records

### 11.1 The method

**Reconciliation** means explaining the difference between two numbers that should agree. Teams do it every month-end: the dashboard says X, finance says Y. A sloppy reconciliation ends with "probably timing". A good one ends with a list of records and a reason for each, and with **explained = 100 percent**. The method has five steps.

1. **Write both numbers with their definitions** (grain, date basis, filters, time zone). Often the mismatch is already visible here.
2. **Align everything you can**: same period, same time zone, same statuses. Remove differences one at a time and watch the gap.
3. **Compare the sets of keys.** For counts, list the keys that are in A but not in B, in B but not in A, and in both.
4. **Classify** each one-sided key by a reason (a rule with a name, not a guess).
5. **Check the arithmetic**: the sum of the classified pieces must equal the gap. If a part stays unexplained, say how large it is, and look at its records.

The key idea: *a number is a sum over records, so the difference between two numbers is a sum over the records that differ.* Never stay at the level of totals.

### 11.2 Tracing a fan-out to the record

A dashboard shows "money collected" of 21.3 million. Finance's ledger says 7.7 million. Nobody trusts either. The first step is to find what the dashboard query does. Suppose its query joins payments to items (the line item table was joined "to show the item type").

```python run
dash = payments.merge(items[["job_id", "line_no"]], on="job_id")           # the dashboard's join
dash_total = dash["amount"].sum()
ledger_total = payments["amount"].sum()
print(f"dashboard : {dash_total:>12,}")
print(f"ledger    : {ledger_total:>12,}")
print(f"gap       : {dash_total - ledger_total:>12,}  (ratio {dash_total / ledger_total:.2f})")
```
```text
dashboard :   21,291,630
ledger    :    7,656,860
gap       :   13,634,770  (ratio 2.78)
```

A ratio of 2.78, close to the average number of lines per job (7,554 / 3,000 = 2.52, weighted towards paid jobs). That is a clue (step 1 of the method), not a proof. We make the proof at the **record** level: compute the amount per job both ways, subtract, and look at the biggest differences.

```python run
per_job = pd.DataFrame({
    "dash": dash.groupby("job_id")["amount"].sum(),
    "ledger": payments.groupby("job_id")["amount"].sum(),
})
per_job["diff"] = per_job["dash"] - per_job["ledger"]
per_job = per_job.join(items.groupby("job_id").size().rename("n_lines"))
print(per_job.sort_values("diff", ascending=False).head(5).to_string())
```
```text
         dash  ledger   diff  n_lines
job_id                               
7650    27200    6800  20400        4
6993    26400    6600  19800        4
5333    26000    6500  19500        4
6659    25600    6400  19200        4
5870    24800    6200  18600        4
```

For every job, the dashboard counts the payments once **per line**. Test the claim exactly:

```python run
explained = per_job["diff"] == (per_job["n_lines"] - 1) * per_job["ledger"]
print("jobs where  diff = (lines - 1) x ledger :", int(explained.sum()), "of", len(per_job))
print("sum of the differences                  :", f"{per_job['diff'].sum():,}")
print("gap between the totals                  :", f"{dash_total - ledger_total:,}")
print("explained share of the gap              :", f"{explained.mean() * 100:.0f} %")
```
```text
jobs where  diff = (lines - 1) x ledger : 2690 of 2690
sum of the differences                  : 13,634,770
gap between the totals                  : 13,634,770
explained share of the gap              : 100 %
```

Every job obeys the rule, the sum of the job differences equals the gap between totals, and the explained share is 100 percent. That is a reconciliation: the dashboard's number is the ledger's number multiplied, job by job, by the number of lines. The fix is a one-line change in the dashboard query (do not join the items), and now the person who owns it knows *why*, and can prove it.

### 11.3 Comparing sets of keys

Not every mismatch is a multiplication. Often two teams count *different sets* of records. Finance counts the jobs for which money arrived in February. Operations counts the jobs completed in February. Both are called "February jobs".

```python run
def compare_keys(a, b, name_a="A", name_b="B"):
    """Return the keys only in A, only in B, in both (as sets), and print the sizes."""
    a, b = set(a), set(b)
    only_a, only_b, both = a - b, b - a, a & b
    print(f"{name_a}: {len(a)} | {name_b}: {len(b)} | in both: {len(both)} | only {name_a}: {len(only_a)} | only {name_b}: {len(only_b)}")
    return only_a, only_b, both


ops = set(jobs.loc[feb(jobs["completed_at"]), "job_id"])
fin = set(payments.loc[feb(payments["paid_at"]), "job_id"])
only_ops, only_fin, both = compare_keys(ops, fin, "ops (completed in Feb)", "finance (paid in Feb)")
```
```text
ops (completed in Feb): 807 | finance (paid in Feb): 829 | in both: 787 | only ops (completed in Feb): 20 | only finance (paid in Feb): 42
```

Two sets with 807 and 829 jobs: a net difference of 22, which hides flows of 20 and 42 jobs in the two directions. Classify the one-sided keys.

```python run
J = jobs.set_index("job_id")
last_pay = payments.groupby("job_id")["paid_at"].max()
first_pay = payments.groupby("job_id")["paid_at"].min()

rows = []
for jid in only_ops:                                          # completed in Feb, but no payment dated in Feb
    if jid not in last_pay.index:
        why = "completed, never paid"
    elif first_pay[jid] >= pd.Timestamp("2025-03-01"):
        why = "completed in Feb, paid in March or later"
    else:
        why = "other"
    rows.append(("only ops", why))
for jid in only_fin:                                          # paid in Feb, but not completed in Feb
    r = J.loc[jid]
    if r["status"] == "pending":
        why = "deposit on a job that is still pending"
    elif r["completed_at"] < pd.Timestamp("2025-02-01"):
        why = "completed in January, paid in February"
    elif r["completed_at"] >= pd.Timestamp("2025-03-01"):
        why = "deposit paid in Feb, completed in March or later"
    else:
        why = "other"
    rows.append(("only finance", why))
cls = pd.DataFrame(rows, columns=["side", "reason"])
print(cls.value_counts().sort_index().to_string())
print("\nunexplained ('other'):", int((cls["reason"] == "other").sum()))
```
```text
side          reason                                          
only finance  completed in January, paid in February              29
              deposit paid in Feb, completed in March or later    13
only ops      completed in Feb, paid in March or later            20

unexplained ('other'): 0
```

Each one-sided job lands in a named reason; "other" is empty, so the difference is explained completely. Each reason is a fact about the business (payments after the work, deposits before the work, work never paid) that a manager can act on. This is what you give to the manager instead of "probably timing".

### 11.4 The bridge

A **bridge** (also called a waterfall) lists the starting number, each effect with its sign, and the ending number. The effects add up exactly to the difference. It is the standard form of a reconciliation report.

```python run
def bridge(start_label, start_value, steps, end_label, end_value):
    rows = [(start_label, start_value)] + steps
    out = pd.DataFrame(rows, columns=["step", "jobs"])
    running = out["jobs"].cumsum()
    out["running_total"] = running
    gap = int(running.iloc[-1] - end_value)
    out.loc[len(out)] = [f"= {end_label} (expected)", end_value, end_value]
    out["check"] = ""
    out.loc[out.index[-1], "check"] = "OK" if gap == 0 else f"UNEXPLAINED {gap:+d}"
    return out


steps = [(f"ops only: {r}", -n) for r, n in cls[cls["side"] == "only ops"]["reason"].value_counts().items()] + \
        [(f"finance only: {r}", +n) for r, n in cls[cls["side"] == "only finance"]["reason"].value_counts().items()]
print(bridge("jobs completed in Feb (ops)", len(ops), steps, "jobs paid in Feb (finance)", len(fin)).to_string(index=False))
```
```text
                                                          step  jobs  running_total check
                                   jobs completed in Feb (ops)   807            807      
            ops only: completed in Feb, paid in March or later   -20            787      
          finance only: completed in January, paid in February    29            816      
finance only: deposit paid in Feb, completed in March or later    13            829      
                       = jobs paid in Feb (finance) (expected)   829            829    OK
```

The bridge goes from 807 to 928 in named steps and closes to zero. A bridge with a non-zero remainder is not a failure: it is a precise statement of what you do not yet understand. Hand that over, and nobody can say you hid it.

## 12. Worked case: total volume against completed plus pending

Now the case of section 1. A dashboard shows, for February, **total volume** (jobs by `created_at`), **completed volume** (jobs by `started_at` with status completed) and **pending volume** (by `started_at` with status pending). The three numbers do not obey `completed + pending = total`: 809 + 0 against 895. We reconcile it fully.

### 12.1 Step 1: write the definitions

| Number | Date basis | Status filter | Value |
|---|---|---|---|
| total volume | `created_at` in Feb | none | 895 |
| completed volume | `started_at` in Feb | `completed` | 809 |
| pending volume | `started_at` in Feb | `pending` | 0 |

The definitions already contradict the hope that the parts add up. The total is by **created**, the parts are by **started**: they are different *populations of jobs*. And two statuses are missing from the table: `cancelled` and `failed`.

### 12.2 Step 2: the sets

Let `T` be the jobs created in February and `C` the jobs started in February with status completed. The gap is not "T minus C" as a number; it is a comparison of two sets.

```python run
T = set(jobs.loc[feb(jobs["created_at"]), "job_id"])
C = set(jobs.loc[feb(jobs["started_at"]) & jobs["status"].eq("completed"), "job_id"])
only_T, only_C, both_TC = compare_keys(T, C, "T created in Feb", "C completed, started in Feb")
```
```text
T created in Feb: 895 | C completed, started in Feb: 809 | in both: 711 | only T created in Feb: 184 | only C completed, started in Feb: 98
```

### 12.3 Step 3: classify each job that is in only one set

```python run
J = jobs.set_index("job_id")


def why_only_T(r):                        # created in Feb, not in the completed-and-started-in-Feb set
    if r["status"] == "cancelled": return "cancelled (never started)"
    if r["status"] == "failed": return "failed"
    if r["status"] == "pending": return "pending (no start date yet)"
    if r["started_at"] >= pd.Timestamp("2025-03-01"): return "started in March or later"
    return "other"


def why_only_C(r):                        # in C but not created in Feb
    if r["created_at"] < pd.Timestamp("2025-02-01"): return "created in January, started in February"
    return "other"


reasons_T = J.loc[sorted(only_T)].apply(why_only_T, axis=1).value_counts()
reasons_C = J.loc[sorted(only_C)].apply(why_only_C, axis=1).value_counts()
print("jobs created in February but NOT in 'completed, started in Feb':")
print(reasons_T.to_string())
print("\njobs in 'completed, started in Feb' but NOT created in February:")
print(reasons_C.to_string())
```
```text
jobs created in February but NOT in 'completed, started in Feb':
started in March or later    87
cancelled (never started)    84
failed                       13

jobs in 'completed, started in Feb' but NOT created in February:
created in January, started in February    98
```

### 12.4 Step 4: the bridge

```python run
steps = [(f"created in Feb, but {k}", -int(v)) for k, v in reasons_T.items()] + \
        [(f"{k}", +int(v)) for k, v in reasons_C.items()]
br = bridge("total volume (created in Feb)", len(T), steps, "completed volume (started in Feb)", len(C))
print(br.to_string(index=False))
```
```text
                                          step  jobs  running_total check
                 total volume (created in Feb)   895            895      
 created in Feb, but started in March or later   -87            808      
 created in Feb, but cancelled (never started)   -84            724      
                    created in Feb, but failed   -13            711      
       created in January, started in February    98            809      
= completed volume (started in Feb) (expected)   809            809    OK
```

The bridge closes. Read it as a story: 895 jobs were created in February.

- **Cancelled** jobs (84) never start, so they cannot be in a "started" count.
- **Failed** jobs (13) are removed by the `completed` filter.
- **87 jobs created late in February started in March** (booked a few days ahead, or simply waiting), so they leave a February "started" count.
- **98 jobs created in January started in February**, so they come in.
- **Pending** jobs do not appear in the bridge for February, because every job created in February has already been decided. They would appear for March (32 jobs). But they explain the *zero* on the dashboard's pending line: a pending job has no start date, so a filter on `started_at` can never select it, in any month.

The net of 86 is the sum of four movements, three leaving and one entering: −87 − 84 − 13 + 98 = −86.

> **Predict the output.** If the dashboard defined all three numbers by `created_at`, with the status as it is today, would `completed + pending + cancelled + failed` equal the total?

<details><summary>Answer</summary>

```python run
cohort = jobs[feb(jobs["created_at"])]
by_status = cohort["status"].value_counts()
print(by_status.to_string())
print("sum:", int(by_status.sum()), "| total created in Feb:", len(cohort), "| equal:", int(by_status.sum()) == len(cohort))
```
```text
status
completed    798
cancelled     84
failed        13
sum: 895 | total created in Feb: 895 | equal: True
```

Yes, exactly, for any month: with **one date basis** (created) and **all statuses**, the statuses partition the cohort, so the parts add up by construction (section 9.1). The dashboard broke the equation by mixing two date bases and by dropping two statuses. The cure is a design rule: *a dashboard that shows "total = part + part + ..." must use one date basis and a complete set of statuses.* Anything else should not show a total next to its parts.

</details>

### 12.5 Step 5: the same bridge in SQL

A reconciliation you can only run in pandas cannot be handed to the dashboard team. The same classification in one SQL statement:

```python run
print(q("""
WITH t AS (
  SELECT job_id,
         CASE WHEN created_at >= '2025-02-01' AND created_at < '2025-03-01' THEN 1 ELSE 0 END AS in_T,
         CASE WHEN status = 'completed' AND started_at >= '2025-02-01' AND started_at < '2025-03-01' THEN 1 ELSE 0 END AS in_C,
         status, created_at, started_at
  FROM jobs)
SELECT CASE
         WHEN in_T = 1 AND in_C = 1 THEN '0 in both'
         WHEN in_T = 1 AND status = 'cancelled' THEN '1 created in Feb, cancelled'
         WHEN in_T = 1 AND status = 'failed' THEN '2 created in Feb, failed'
         WHEN in_T = 1 AND status = 'pending' THEN '3 created in Feb, pending'
         WHEN in_T = 1 THEN '4 created in Feb, started later'
         ELSE '5 created before Feb, started in Feb' END AS bucket,
       COUNT(*) AS jobs
FROM t
WHERE in_T = 1 OR in_C = 1
GROUP BY bucket ORDER BY bucket
""").to_string(index=False))
```
```text
                              bucket  jobs
                           0 in both   711
         1 created in Feb, cancelled    84
            2 created in Feb, failed    13
     4 created in Feb, started later    87
5 created before Feb, started in Feb    98
```

The same buckets, from the database, with the buckets numbered so they sort in a readable order. Bucket 3 (pending) is absent because no February job is pending; the query would show it for March. Run the pandas version and the SQL version side by side: if both agree, the explanation is solid.

### 12.6 Step 6: what to change

Reconciliation is not finished until something changes. Three options, from the lightest.

1. **Rename the numbers**: "Created volume", "Completed volume (by start date)". The reader no longer expects them to add up.
2. **Remove the false total**: do not show a total beside parts that use another basis.
3. **Rebuild on one basis**: choose a cohort view (everything by `created_at`; the statuses add up) *or* an activity view (everything by the date of the event: created, started, completed). Say which one the dashboard is.

With an activity view, "work started in February" and "work completed in February" are legitimate metrics, and *no one expects them to add up to jobs created*. With a cohort view, statuses can change tomorrow (a pending job completes); say "as of" when.

## 13. A reusable toolkit

The functions of this chapter fit in a short toolkit. You will reuse them in da.07 (SQL for analysts) and in every project.

```python run
def assert_rows_unchanged(before, after, label=""):
    """Call after every join: the row count must not move unless you expect it to."""
    if len(before) != len(after):
        raise AssertionError(f"{label}: rows changed {len(before)} -> {len(after)} (fan-out or a lost key?)")
    return after


def safe_join(left, right, on, how="left", validate="m:1", label=""):
    """A join that checks the relationship and the row count."""
    out = left.merge(right, on=on, how=how, validate=validate)
    if how == "left":
        assert_rows_unchanged(left, out, label or f"join on {on}")
    return out


def explain_gap(name_a, a, name_b, b):
    """One-line statement of two numbers, their difference and the ratio."""
    print(f"{name_a} = {a:,} | {name_b} = {b:,} | gap = {a - b:+,} | ratio = {a / b if b else float('nan'):.3f}")


# 1. good join passes
ok = safe_join(jobs, customers[["customer_id", "city"]], on="customer_id", label="jobs + customers")
print("jobs + customers:", len(ok), "rows")
# 2. wrong join is caught
try:
    safe_join(jobs, payments, on="job_id", label="jobs + payments", validate="1:m")
except AssertionError as e:
    print("AssertionError:", e)
# 3. the same wrong join as m:1 is caught by pandas itself
try:
    safe_join(jobs, payments, on="job_id", label="jobs + payments")
except Exception as e:
    print(type(e).__name__, ":", str(e).splitlines()[0])
explain_gap("dashboard", int(dash_total), "ledger", int(ledger_total))
```
```text
jobs + customers: 3000 rows
AssertionError: jobs + payments: rows changed 3000 -> 3546 (fan-out or a lost key?)
MergeError : Merge keys are not unique in right dataset; not a many-to-one merge
dashboard = 21,291,630 | ledger = 7,656,860 | gap = +13,634,770 | ratio = 2.781
```

The two layers of protection are complementary: `validate=` checks the *relationship* (is the right side unique?) and `assert_rows_unchanged` checks the *outcome* (did the row count move?). With `validate="1:m"` the left-join row count grows as it should for a one-to-many, but you asserted the opposite expectation (no change), so the assertion fires. Choose the check that states what you expect.

A last piece is a **pre-flight checklist** before you share a number:

1. What is one row of each table I use? (`check_grain`)
2. What are the relationships, and did every join keep or intentionally change the row count?
3. Which date and time zone does each metric use?
4. What is in the numerator and denominator; is the numerator a subset of the denominator?
5. Are the statuses a partition; do the parts add up to the total on one basis?
6. Does a second method (SQL against pandas, or an independent query) give the same number?
7. If a number is a rate, do I show the counts behind it?
8. Is the period complete and mature?


## 14. Project: metric definitions and a reconciliation report

**The brief.** The management of QuickFix argue every month about the numbers. You are asked for two documents that end the arguments:

1. A **metric definition document**: every metric the company reports, defined without ambiguity, and **computed from that definition** for January, February and March.
2. A **reconciliation report**: for the two disagreements that cause the most trouble ("total volume against completed plus pending", and "cash collected against completed work"), a bridge that explains the gap record by record.

Everything is produced by code, so that the documents cannot disagree with the numbers. The company reports in **IST**, so the first step is to move every timestamp to IST once, at the border, and to say so.

### 14.1 Step 1: the grain sheet and the clean border

```python run
def to_ist(df, cols):
    out = df.copy()
    for c in cols:
        out[c] = out[c] + IST
    return out


jobs_i = to_ist(jobs, ["created_at", "started_at", "completed_at", "cancelled_at"])
pay_i = to_ist(payments, ["paid_at"])
ref_i = to_ist(refunds, ["refunded_at"])

grain_sheet = pd.DataFrame([
    ("customers", "customer", "customer_id", len(customers), customers["customer_id"].is_unique),
    ("jobs", "job", "job_id", len(jobs_i), jobs_i["job_id"].is_unique),
    ("items", "line item of a job", "job_id + line_no", len(items), not items.duplicated(["job_id", "line_no"]).any()),
    ("payments", "payment", "payment_id", len(pay_i), pay_i["payment_id"].is_unique),
    ("refunds", "refund", "refund_id", len(ref_i), ref_i["refund_id"].is_unique),
], columns=["table", "one row per", "key", "rows", "key is unique"])
print(grain_sheet.to_string(index=False))
print()
print("jobs without a known customer:", int((~jobs_i["customer_id"].isin(customers["customer_id"])).sum()))
print("payments without a known job :", int((~pay_i["job_id"].isin(jobs_i["job_id"])).sum()))
print("refunds without a known job  :", int((~ref_i["job_id"].isin(jobs_i["job_id"])).sum()))
print("lifecycle problems           :", lifecycle_problems(jobs_i))
```
```text
    table        one row per              key  rows  key is unique
customers           customer      customer_id   800           True
     jobs                job           job_id  3000           True
    items line item of a job job_id + line_no  7554           True
 payments            payment       payment_id  3236           True
  refunds             refund        refund_id   134           True

jobs without a known customer: 0
payments without a known job : 0
refunds without a known job  : 0
lifecycle problems           : {'completed without completed_at': 0, 'completed_at on a non-completed job': 0, 'cancelled without cancelled_at': 0, 'cancelled but started': 0, 'completed before it started': 0, 'started before it was created': 0}
```

The sheet shows the grain, the key, and that the key is unique. It also runs the orphan tests and the lifecycle test of section 9. All clean, so the data is fit for use. If any line failed, the report would start with that failure.

### 14.2 Step 2: the definitions, as data

Each metric is one entry with its text and its computation. The function returns the value *and* its numerator and denominator, so a rate is never shown without the counts.

```python run
@dataclass(frozen=True)
class MetricSpec:
    name: str
    question: str
    unit: str
    date_basis: str
    includes: str
    excludes: str
    fn: Callable                                   # fn(ctx, start, end) -> (value, numerator, denominator)


def month_mask(s, start, end):
    return (s >= start) & (s < end)


def _count(ctx, start, end, col, extra=None):
    m = month_mask(ctx["jobs"][col], start, end)
    if extra is not None:
        m &= extra(ctx["jobs"])
    n = int(m.sum())
    return n, n, None


def _rate(ctx, start, end, num, den):
    j = ctx["jobs"]
    cohort = month_mask(j["created_at"], start, end) & den(j)
    top = int((cohort & num(j)).sum())
    bottom = int(cohort.sum())
    return top / bottom, top, bottom


SPECS = [
    MetricSpec("jobs_created", "How much demand arrived?", "jobs", "created_at (IST)", "all statuses", "none",
               lambda c, s, e: _count(c, s, e, "created_at")),
    MetricSpec("jobs_started", "How much work began?", "jobs", "started_at (IST)", "jobs with an actual start", "scheduled but not started, cancelled",
               lambda c, s, e: _count(c, s, e, "started_at")),
    MetricSpec("jobs_completed", "How much work finished?", "jobs", "completed_at (IST)", "status completed", "cancelled, failed, pending",
               lambda c, s, e: _count(c, s, e, "completed_at", lambda j: j["status"].eq("completed"))),
    MetricSpec("completion_rate", "Of the demand that arrived and was decided, how much was finished?", "share of jobs",
               "created_at (IST), cohort", "jobs created in the month, status completed / (all but pending)", "pending jobs (not decided yet)",
               lambda c, s, e: _rate(c, s, e, lambda j: j["status"].eq("completed"), lambda j: ~j["status"].eq("pending"))),
    MetricSpec("cancellation_rate", "How much of the demand falls away?", "share of jobs",
               "created_at (IST), cohort", "jobs created in the month, status cancelled / all", "none",
               lambda c, s, e: _rate(c, s, e, lambda j: j["status"].eq("cancelled"), lambda j: pd.Series(True, index=j.index))),
    MetricSpec("completed_value", "How much work was finished, in money?", "rupees (quote)", "completed_at (IST)",
               "quote_total of completed jobs", "refunds are not subtracted",
               lambda c, s, e: (lambda m: (int(c["jobs"].loc[m, "quote_total"].sum()), int(c["jobs"].loc[m, "quote_total"].sum()), None))(
                   month_mask(c["jobs"]["completed_at"], s, e) & c["jobs"]["status"].eq("completed"))),
    MetricSpec("avg_ticket", "What does a typical finished job cost?", "rupees per completed job", "completed_at (IST)",
               "completed_value / jobs_completed", "cancelled, failed, pending",
               lambda c, s, e: (lambda m: (c["jobs"].loc[m, "quote_total"].mean(), int(c["jobs"].loc[m, "quote_total"].sum()), int(m.sum())))(
                   month_mask(c["jobs"]["completed_at"], s, e) & c["jobs"]["status"].eq("completed"))),
    MetricSpec("cash_collected", "How much money arrived?", "rupees", "paid_at (IST)", "all payments (deposit, full, balance)", "refunds are not subtracted",
               lambda c, s, e: (lambda v: (v, v, None))(int(c["pay"].loc[month_mask(c["pay"]["paid_at"], s, e), "amount"].sum()))),
    MetricSpec("refunds_issued", "How much money went back?", "rupees", "refunded_at (IST)", "all refunds", "none",
               lambda c, s, e: (lambda v: (v, v, None))(int(c["ref"].loc[month_mask(c["ref"]["refunded_at"], s, e), "amount"].sum()))),
    MetricSpec("active_customers", "How many different customers asked for work?", "customers", "created_at (IST)",
               "distinct customers with a job created in the month", "customers with no job that month",
               lambda c, s, e: (lambda v: (v, v, None))(int(c["jobs"].loc[month_mask(c["jobs"]["created_at"], s, e), "customer_id"].nunique()))),
]
print(len(SPECS), "metrics defined:", [m.name for m in SPECS])
```
```text
10 metrics defined: ['jobs_created', 'jobs_started', 'jobs_completed', 'completion_rate', 'cancellation_rate', 'completed_value', 'avg_ticket', 'cash_collected', 'refunds_issued', 'active_customers']
```

### 14.3 Step 3: compute them, with the counts

```python run
ctx = {"jobs": jobs_i, "pay": pay_i, "ref": ref_i}
months = {"Jan": ("2025-01-01", "2025-02-01"), "Feb": ("2025-02-01", "2025-03-01"), "Mar": ("2025-03-01", "2025-04-01")}


def metrics_table(ctx, specs, months):
    rows = []
    for m in specs:
        row = {"metric": m.name}
        for label, (s, e) in months.items():
            value, num, den = m.fn(ctx, pd.Timestamp(s), pd.Timestamp(e))
            if m.unit.startswith("share"):
                row[label] = f"{value * 100:5.1f}%  ({num:,}/{den:,})"
            elif isinstance(value, float):
                row[label] = f"{value:,.0f}"
            else:
                row[label] = f"{value:,}"
        rows.append(row)
    return pd.DataFrame(rows)


mt = metrics_table(ctx, SPECS, months)
print(mt.to_string(index=False))
```
```text
           metric                 Jan               Feb                 Mar
     jobs_created               1,031               895               1,066
     jobs_started                 860               818                 980
   jobs_completed                 839               803                 961
  completion_rate  91.0%  (938/1,031)  89.3%  (799/895)  90.3%  (935/1,036)
cancellation_rate    7.1%  (73/1,031)    9.4%  (84/895)    7.8%  (83/1,066)
  completed_value           2,369,400         2,251,200           2,818,800
       avg_ticket               2,824             2,803               2,933
   cash_collected           2,310,340         2,258,800           2,826,630
   refunds_issued              63,580            59,550              88,460
 active_customers                 565               549                 591
```

Note how each rate shows its counts, and how each date metric names its basis. Look at the cohort rates for March: the completion rate excludes the 30 jobs created in March (IST) that are still pending (they are not decided), and the table says so in the definition. Compare with section 8.4: the data of the immature weeks would otherwise drag the rate down.

Two independent checks keep the table honest. First, the cohort statuses partition the month. Second, a second engine gives the same numbers.

```python run
for label, (s, e) in months.items():
    cohort = jobs_i[month_mask(jobs_i["created_at"], pd.Timestamp(s), pd.Timestamp(e))]
    parts = cohort["status"].value_counts()
    assert parts.sum() == len(cohort), "statuses do not partition the cohort"
print("statuses partition every monthly cohort: OK")

# second engine: SQL on the same (UTC) data, month borders shifted to IST in SQL
sql_counts = q("""
SELECT strftime('%Y-%m', datetime(created_at, '+330 minutes')) AS month, COUNT(*) AS jobs_created
FROM jobs GROUP BY month ORDER BY month
""")
ours = {m: int(mt.loc[mt["metric"] == "jobs_created", m].iloc[0].replace(",", "")) for m in ("Jan", "Feb", "Mar")}
sql = dict(zip(["Jan", "Feb", "Mar", "Apr"], sql_counts["jobs_created"]))
print("SQL    :", sql)
print("pandas :", ours)
print("match for Jan-Mar:", all(sql[m] == ours[m] for m in ours))
```
```text
statuses partition every monthly cohort: OK
SQL    : {'Jan': 1031, 'Feb': 895, 'Mar': 1066, 'Apr': 8}
pandas : {'Jan': 1031, 'Feb': 895, 'Mar': 1066}
match for Jan-Mar: True
```

Both engines agree. The SQL result has one more row that the table does not report: **8 jobs created in April, in IST**. They were created between 18:30 and 24:00 UTC on 31 March, which is already 1 April in India. Three of the monthly counts add up to 2,992, and the eight explain the missing jobs from the 3,000. This is the time zone effect of section 8.3 caught by the second engine; with only one engine, the 8 jobs would have vanished from the report without a trace.

### 14.4 Step 4: the first reconciliation, as a function

The bridge of section 12 is generalised for any month, so the report can include all three.

```python run
def volume_bridge(j, start, end):
    """Bridge from 'jobs created in the month' to 'jobs completed, started in the month' (IST dates)."""
    T = j[month_mask(j["created_at"], start, end)]
    Cm = j[month_mask(j["started_at"], start, end) & j["status"].eq("completed")]
    only_T = T[~T["job_id"].isin(Cm["job_id"])]
    only_C = Cm[~Cm["job_id"].isin(T["job_id"])]
    name = lambda r: ("cancelled (never started)" if r["status"] == "cancelled" else
                      "failed" if r["status"] == "failed" else
                      "pending (no start date yet)" if r["status"] == "pending" else
                      "started after the month")
    out = only_T.apply(name, axis=1).value_counts()
    steps = [(f"created in month, {k}", -int(v)) for k, v in out.items()]
    steps += [("created before the month, started in it", len(only_C))]
    return bridge("total volume (created in month)", len(T), steps, "completed volume (started in month)", len(Cm))


for label, (s, e) in months.items():
    b = volume_bridge(jobs_i, pd.Timestamp(s), pd.Timestamp(e))
    print(f"--- {label} ---")
    print(b[["step", "jobs", "running_total", "check"]].to_string(index=False))
```
```text
--- Jan ---
                                            step  jobs  running_total check
                 total volume (created in month)  1031           1031      
       created in month, started after the month   -97            934      
     created in month, cancelled (never started)   -73            861      
                        created in month, failed   -20            841      
         created before the month, started in it     0            841      
= completed volume (started in month) (expected)   841            841    OK
--- Feb ---
                                            step  jobs  running_total check
                 total volume (created in month)   895            895      
       created in month, started after the month   -90            805      
     created in month, cancelled (never started)   -84            721      
                        created in month, failed   -12            709      
         created before the month, started in it    97            806      
= completed volume (started in month) (expected)   806            806    OK
--- Mar ---
                                            step  jobs  running_total check
                 total volume (created in month)  1066           1066      
     created in month, cancelled (never started)   -83            983      
       created in month, started after the month   -62            921      
   created in month, pending (no start date yet)   -30            891      
                        created in month, failed   -18            873      
         created before the month, started in it    90            963      
= completed volume (started in month) (expected)   963            963    OK
```

Three months, three closed bridges (every line `OK`). January starts with an effect that is missing in the others, since nothing was created before 1 January in our data: the "created before the month" line is zero. March shows the 30 pending jobs. A reader who sees the three bridges together understands why no month's "completed" equals its "total".

### 14.5 Step 5: the second reconciliation, cash against work

Finance asks: "February completed work is worth X, but February cash is Y. Where is the difference?" The answer is in the payment records. We cut money, not jobs: every rupee of the completed value, and every rupee of cash, is placed in a named bucket.

```python run
s_, e_ = pd.Timestamp("2025-02-01"), pd.Timestamp("2025-03-01")
done_feb = jobs_i[month_mask(jobs_i["completed_at"], s_, e_) & jobs_i["status"].eq("completed")]
value = int(done_feb["quote_total"].sum())
cash = int(pay_i.loc[month_mask(pay_i["paid_at"], s_, e_), "amount"].sum())

p = pay_i.merge(jobs_i[["job_id", "status", "completed_at"]], on="job_id", validate="m:1")
p["in_feb"] = month_mask(p["paid_at"], s_, e_)
p["job_done_feb"] = p["job_id"].isin(done_feb["job_id"])

# money on the jobs completed in February, split by when it was paid
on_done = p[p["job_done_feb"]]
paid_before = int(on_done.loc[on_done["paid_at"] < s_, "amount"].sum())
paid_in = int(on_done.loc[on_done["in_feb"], "amount"].sum())
paid_after = int(on_done.loc[on_done["paid_at"] >= e_, "amount"].sum())
unpaid = value - paid_before - paid_in - paid_after

# February cash that belongs to jobs completed in other months
other = p[p["in_feb"] & ~p["job_done_feb"]]
cash_earlier = int(other.loc[other["completed_at"] < s_, "amount"].sum())
cash_later = int(other.loc[other["completed_at"] >= e_, "amount"].sum())
cash_pending = int(other.loc[other["status"].eq("pending"), "amount"].sum())
cash_other = int(other["amount"].sum()) - cash_earlier - cash_later - cash_pending

steps = [("Feb-completed jobs: deposit paid BEFORE February", -paid_before),
         ("Feb-completed jobs: paid AFTER February", -paid_after),
         ("Feb-completed jobs: not paid yet (at extraction)", -unpaid),
         ("Feb cash on jobs completed EARLIER (balances)", cash_earlier),
         ("Feb cash on jobs completed LATER (deposits)", cash_later),
         ("Feb cash on jobs still pending (deposits)", cash_pending),
         ("Feb cash on other jobs", cash_other)]
bm = bridge("completed value, February (rupees)", value, [(a, b) for a, b in steps], "cash collected, February", cash)
bm["jobs"] = bm["jobs"].map("{:,}".format)
bm["running_total"] = bm["running_total"].map("{:,}".format)
bm = bm.rename(columns={"jobs": "rupees"})
print(bm.to_string(index=False))
```
```text
                                            step    rupees running_total check
              completed value, February (rupees) 2,251,200     2,251,200      
Feb-completed jobs: deposit paid BEFORE February   -17,130     2,234,070      
         Feb-completed jobs: paid AFTER February   -63,490     2,170,580      
Feb-completed jobs: not paid yet (at extraction)         0     2,170,580      
   Feb cash on jobs completed EARLIER (balances)    76,190     2,246,770      
     Feb cash on jobs completed LATER (deposits)    12,030     2,258,800      
       Feb cash on jobs still pending (deposits)         0     2,258,800      
                          Feb cash on other jobs         0     2,258,800      
           = cash collected, February (expected) 2,258,800     2,258,800    OK
```

The bridge closes to the rupee. Read the lines: of the 2,251,200 rupees of work completed in February, 17,130 had been paid as a deposit **before** February, and 63,490 is paid only **after** February (balances that arrive in March). February cash also contains 76,190 of balances for January work, and 12,030 of deposits for work that happens later. The three empty lines are results as well: no February job is still unpaid at the extraction, no pending job paid a deposit in February, and no payment belongs to a cancelled or failed job. That is a statement the finance team can check. Each non-zero line is a lever the business can pull (collect balances faster, ask for deposits earlier) and each has a list of job ids behind it.

> **Try it.** The cash number counts **gross** payments. What is the *net* cash for February (payments minus refunds issued in February)? How does the refund timing differ from the payment timing, and which date basis does `refunds_issued` use?

<details><summary>Answer</summary>

```python run
refunds_feb = int(ref_i.loc[month_mask(ref_i["refunded_at"], s_, e_), "amount"].sum())
print("cash collected :", f"{cash:,}")
print("refunds issued :", f"{refunds_feb:,}")
print("net cash       :", f"{cash - refunds_feb:,}")
late = ref_i.merge(jobs_i[["job_id", "completed_at"]], on="job_id", validate="1:1")
same_month = month_mask(late["refunded_at"], s_, e_) & month_mask(late["completed_at"], s_, e_)
print("refunds issued in Feb on jobs completed in Feb:", int(same_month.sum()), "of", int(month_mask(late["refunded_at"], s_, e_).sum()))
```
```text
cash collected : 2,258,800
refunds issued : 59,550
net cash       : 2,199,250
refunds issued in Feb on jobs completed in Feb: 31 of 35
```

A refund is issued three days after the completion of the job (in this data). Most February refunds (31 of 35) belong to February work, but 4 belong to January jobs completed at the end of January. The `refunds_issued` metric is by `refunded_at`, the money-movement date, like `cash_collected` is by `paid_at`. Both are *cash-basis* metrics. If finance wants "revenue earned in February, net of refunds on that work", that is a third metric with a third date basis (the completion date), and it needs a name of its own: `net_completed_value`. Do not let two metrics share a name because they share a table.

</details>

### 14.6 Step 6: assemble the document

The last step prints the document: the grain sheet, the definitions, the numbers and the bridges, plus the **open issues** that a careful analyst found and does not hide.

```python run
def definition_doc(specs):
    lines = ["# QuickFix: metric definitions (v1)", "",
             "All dates are IST (UTC+05:30). A month is a half-open interval [first day, first day of next month).", ""]
    for m in specs:
        lines += [f"### {m.name}", f"- Question: {m.question}", f"- Unit: {m.unit}", f"- Date basis: {m.date_basis}",
                  f"- Includes: {m.includes}", f"- Excludes: {m.excludes}", ""]
    return "\n".join(lines)


doc = definition_doc(SPECS)
print("\n".join(doc.splitlines()[:16]))
print("...")
print("lines in the definition document:", len(doc.splitlines()))
```
```text
# QuickFix: metric definitions (v1)

All dates are IST (UTC+05:30). A month is a half-open interval [first day, first day of next month).

### jobs_created
- Question: How much demand arrived?
- Unit: jobs
- Date basis: created_at (IST)
- Includes: all statuses
- Excludes: none

### jobs_started
- Question: How much work began?
- Unit: jobs
- Date basis: started_at (IST)
- Includes: jobs with an actual start
...
lines in the definition document: 73
```

```python run
issues = [
    "failed jobs have no failed_at timestamp: no metric can be placed by failure date, and 'open jobs at date X' is an upper bound (9.3).",
    "pending jobs have no start date: metrics by started_at can never include them (12.4).",
    "the newest cohorts are immature: the March completion rate excludes pending jobs; compare it only with cohorts older than 14 days (8.4).",
    "April holds 5 days of data: it is not reported (8.5).",
    "refunds are cash-basis (by refunded_at); a revenue-basis net metric is not defined yet (14.5).",
]
print("Open issues")
for i, t in enumerate(issues, 1):
    print(f"{i}. {t}")
```
```text
Open issues
1. failed jobs have no failed_at timestamp: no metric can be placed by failure date, and 'open jobs at date X' is an upper bound (9.3).
2. pending jobs have no start date: metrics by started_at can never include them (12.4).
3. the newest cohorts are immature: the March completion rate excludes pending jobs; compare it only with cohorts older than 14 days (8.4).
4. April holds 5 days of data: it is not reported (8.5).
5. refunds are cash-basis (by refunded_at); a revenue-basis net metric is not defined yet (14.5).
```

### 14.7 What to hand in

For your own business or dataset, deliver the following.

1. A **grain sheet**: every table, its grain, key, a uniqueness test and the orphan tests.
2. A **metric document**: each metric with question, unit, date basis, time zone, inclusions, exclusions, and a function that computes it and returns the numerator and denominator.
3. The **numbers** for at least three periods, with a second engine (SQL or a second pandas path) that agrees.
4. At least **two reconciliation bridges** that close to zero, each with the list of record ids behind every line.
5. A list of **open issues** and data gaps, honestly stated.
6. A test or an assertion for each rule you rely on (partition of statuses, unique keys, row counts after joins).

## 15. Common traps

| Trap | What happens | Fix |
|---|---|---|
| Counting rows of a table with a finer grain | "7,554 jobs" from the items table | state the grain; `nunique` on the entity key (2.2, 5.1) |
| Summing a job-level value after a join to lines | the sum is inflated, 2.8 times here | aggregate to the grain first, then join (2.2, 4.3) |
| Averages of a job-level value after the join | jobs with many lines are overweighted | compute before the join, or deduplicate (4.2) |
| Left join "to be safe" | right-side duplicates still multiply rows | `validate="m:1"`, compare row counts (4.5, 13) |
| Many-to-many join | rows multiply in both directions | find which side should be unique, aggregate (4.4) |
| Summing distinct counts | repeated customers counted again | recompute `nunique` at each level (5.2) |
| `COUNT(col)` read as `COUNT(*)` | nulls are skipped | choose on purpose (5.1, 10.1) |
| Average of averages | wrong when group sizes differ | add numerators and denominators, divide once (6.1) |
| Weighting by `size` when values are missing | missing values carry weight | weight by `count` (6.3) |
| Comparing groups with different mixes | Simpson's paradox | compare within a kind, or standardise (6.4) |
| A rate whose numerator is not a subset of its denominator | a quotient that is not a share | check the subset rule (7.2) |
| A metric name that hides the definition | three Februaries | name, basis and unit in the name and the document (7.1, 7.4) |
| `<= last day` for a month end | the last day loses its afternoon | half-open intervals (8.2) |
| UTC against local month borders | different job sets in each month | convert once at the border; state the zone (8.3) |
| Newest period compared with old ones | immature cohorts look worse | compare mature cohorts; show pending (8.4) |
| Partial period shown beside full ones | false drop | label or drop it (8.5) |
| Filtering on a date that can be null | rows silently vanish (pending jobs in a "started" filter) | know which statuses have the date (1.2, 9.2, 10.2) |
| A total next to parts on another basis | parts do not add up | one basis, all statuses, or rename (12.6) |
| Status trusted without the timestamps | contradictions between the two | lifecycle checks (9.2) |
| Rebuilding history from a snapshot | numbers are only bounds | keep event logs; say "upper bound" (9.3) |
| Stopping at "probably timing" | no one can act | key sets, named reasons, bridge to 100 percent (11) |
| One engine only | a bug in the logic goes unnoticed | compute in pandas and SQL, compare (10.6) |

A debugging habit for every number that looks wrong: print the **grain**, the **row count** before and after each step, the **date basis**, and the **list of statuses** that the number includes. Almost every wrong number in this chapter is visible in those four things.

## 16. Summary

- **A number is a promise about a definition.** Most disagreements are not bugs: two people computed different things under one name. The skill is to ask what is counted, when, and in what zone, before you write code.
- **Grain** is "what does one row represent". State it for every table and every result, test it (`check_grain`, uniqueness of the key including null keys), and remember that a column has the grain of the table where it was born. A table is an entity, an event, a line or a snapshot.
- **Keys and relationships** (one-to-one, one-to-many, many-to-one, many-to-many) must be tested, not assumed. Test the parent key, the orphans, and the relationship before each join.
- **Fan-out** multiplies counts, sums and averages of the "one" side when you join it to the "many" side. The cure is *aggregate to the grain first, then join*, validate the relationship (`validate=`), and compare row counts. SQL has the same rule, in CTEs.
- **Counts**: `COUNT(*)`, `COUNT(col)` and `COUNT(DISTINCT col)` answer three questions. Distinct counts are not additive across groups that can overlap. Every percentage has a denominator; name it.
- **Averages**: never average averages or rates; add numerators and denominators, then divide. Choose the unit (per job, per customer). Beware of Simpson's paradox: compare within strata or standardise.
- **Metric definitions** list name, question, grain, numerator, denominator, date basis, time zone, inclusions, exclusions, unit, owner and version. A rate's numerator must be a subset of its denominator. Keep text and code together, in one place, and show the counts behind every rate.
- **Dates**: pick the basis on purpose (created, started, completed, paid); use half-open intervals; convert time zones once, at the border; do not compare immature cohorts or partial periods without a label.
- **Status** is a state: a partition of the entities (mutually exclusive, exhaustive) only for one date basis. Check it against the timestamps; a snapshot cannot rebuild history exactly.
- **Reconciliation** is explaining the difference between two numbers *record by record*: align the definitions, compare the key sets, classify each one-sided key by a named reason, and close the bridge to zero. The worked case shows why "completed plus pending" is not the total: different date bases, missing statuses, and a status with no start date.
- **Work two ways.** A second engine (pandas and SQL) is the cheapest insurance there is.

You reached the three outcomes of this chapter: you can **state the grain** of any table before analysing it (and prove it with a test), you can **write a metric definition** that two people compute identically, and you can **trace a total mismatch down to the individual records** that cause it, with a bridge that closes to zero. Next, da.07 takes the SQL side much further: window functions, cohort, funnel and retention queries, and DuckDB on pandas and Parquet, all of which depend on the grain and metric discipline you practised here.
