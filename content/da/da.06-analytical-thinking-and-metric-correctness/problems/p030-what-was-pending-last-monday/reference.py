import pandas as pd


def pending_on(jobs, when):
    when = pd.Timestamp(when)
    created = jobs["created_at"] <= when
    done = jobs["completed_at"].notna() & (jobs["completed_at"] <= when)
    cancelled = jobs["cancelled_at"].notna() & (jobs["cancelled_at"] <= when)
    return sorted(int(j) for j in jobs.loc[created & ~done & ~cancelled, "job_id"])
