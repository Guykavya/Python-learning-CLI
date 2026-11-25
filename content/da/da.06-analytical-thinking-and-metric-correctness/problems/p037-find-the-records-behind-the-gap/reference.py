import pandas as pd


def explain_gap(dashboard, sql_result):
    d_sum = dashboard.groupby("job_id")["amount"].sum()
    s_sum = sql_result.groupby("job_id")["amount"].sum()
    d_rows = dashboard.groupby("job_id").size()
    s_rows = sql_result.groupby("job_id").size()
    diff = d_sum.sub(s_sum, fill_value=0)
    gap = int(dashboard["amount"].sum() - sql_result["amount"].sum())
    by_job, reasons = {}, {}
    for job_id in sorted(diff.index):
        c = int(diff[job_id])
        if c == 0:
            continue
        job_id = int(job_id)
        by_job[job_id] = c
        if job_id not in s_sum.index:
            reasons[job_id] = "only in dashboard"
        elif job_id not in d_sum.index:
            reasons[job_id] = "only in sql result"
        elif d_rows[job_id] != s_rows[job_id]:
            reasons[job_id] = f"repeated rows: {int(d_rows[job_id])} rows in dashboard, {int(s_rows[job_id])} rows in sql result"
        else:
            reasons[job_id] = "amount differs"
    return {"gap": gap, "by_job": by_job, "reasons": reasons, "unexplained": gap - sum(by_job.values())}
