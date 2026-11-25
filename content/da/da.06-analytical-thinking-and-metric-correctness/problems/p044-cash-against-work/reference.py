import pandas as pd

LABELS = [
    "completed in month, paid before the month",
    "completed in month, paid after the month",
    "completed in month, not paid yet",
    "paid in month, job completed earlier",
    "paid in month, job completed later or pending",
    "paid in month, other jobs",
    "refunds issued in month",
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
