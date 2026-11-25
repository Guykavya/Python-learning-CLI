## Approach

Split the money, not the jobs. The work value of the period splits into what was paid **before**, **inside** and **after**
the period, plus what is **not paid yet**. The cash of the period splits into the part that belongs to work finished
inside it (already counted in "inside") and the part that belongs to other jobs: finished earlier (balances), finished later
or still pending (deposits), or other (cancelled or failed jobs). Subtract what leaves the work value, add what enters the
cash, take off the refunds, and the bridge closes by arithmetic:
`work = before + inside + after + unpaid`, so `work - before - after - unpaid = inside`, and `inside + earlier + later + other = cash_gross`.

## Code

```python
import pandas as pd

LABELS = [
    "completed in month, paid before the month", "completed in month, paid after the month",
    "completed in month, not paid yet", "paid in month, job completed earlier",
    "paid in month, job completed later or pending", "paid in month, other jobs", "refunds issued in month",
]


def cash_vs_work(jobs, payments, refunds, start, end):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    done = jobs[jobs["status"].eq("completed") & (jobs["completed_at"] >= start) & (jobs["completed_at"] < end)]
    work_value = int(done["quote_total"].sum())
    done_ids = set(done["job_id"])
    p = payments.merge(jobs[["job_id", "status", "completed_at"]], on="job_id", how="left", validate="m:1")
    inside = (p["paid_at"] >= start) & (p["paid_at"] < end)
    on_done = p["job_id"].isin(done_ids)
    before = p[on_done & (p["paid_at"] < start)]
    after = p[on_done & (p["paid_at"] >= end)]
    paid_inside_done = p[on_done & inside]
    other = p[inside & ~on_done]
    earlier = other[other["completed_at"] < start]
    later = other[(other["completed_at"] >= end) | other["status"].eq("pending")]
    rest = other[~other.index.isin(earlier.index) & ~other.index.isin(later.index)]
    r_in = refunds[(refunds["refunded_at"] >= start) & (refunds["refunded_at"] < end)]
    paid_total = p[on_done].groupby("job_id")["amount"].sum()
    unpaid_jobs = done.loc[done["quote_total"] > done["job_id"].map(paid_total).fillna(0), "job_id"]
    unpaid = work_value - int(before["amount"].sum()) - int(paid_inside_done["amount"].sum()) - int(after["amount"].sum())
    amounts = [-int(before["amount"].sum()), -int(after["amount"].sum()), -unpaid,
               int(earlier["amount"].sum()), int(later["amount"].sum()), int(rest["amount"].sum()), -int(r_in["amount"].sum())]
    ids_of = lambda frame: sorted(int(j) for j in frame["job_id"].unique())
    ids = dict(zip(LABELS, [ids_of(before), ids_of(after), sorted(int(j) for j in unpaid_jobs),
                            ids_of(earlier), ids_of(later), ids_of(rest), ids_of(r_in)]))
    cash_gross = int(p.loc[inside, "amount"].sum())
    refunds_total = int(r_in["amount"].sum())
    net = cash_gross - refunds_total
    return {"work_value": work_value, "cash_gross": cash_gross, "refunds": refunds_total, "net_cash": net,
            "steps": list(zip(LABELS, amounts)), "ids": ids, "closes": work_value + sum(amounts) == net}
```

## Complexity

O(n + m): one merge of payments to jobs (`validate="m:1"`: the job table is unique on `job_id`), a few boolean masks and
one group-by.

## Another way

Give every payment a single bucket label with `np.select` (conditions in a fixed order) and add up amounts with
`groupby`; the "not paid yet" line is then the remainder. Pass the seven lines to the `bridge` function of problem 38
for a printed report. The chapter's version uses a separate refund step in a "Try it" and calls it a *cash-basis* metric:
refunds follow `refunded_at`, not the completion date of the work.
