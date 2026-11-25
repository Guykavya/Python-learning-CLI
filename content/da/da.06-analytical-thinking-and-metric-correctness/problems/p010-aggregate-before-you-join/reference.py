def paid_per_customer(jobs, payments):
    paid_by_job = payments.groupby("job_id")["amount"].sum().rename("paid")
    per_job = jobs.merge(paid_by_job, on="job_id", how="left", validate="1:1")
    per_job["paid"] = per_job["paid"].fillna(0)
    out = per_job.groupby("customer_id").agg(quoted=("quote_total", "sum"), paid=("paid", "sum"))
    return out.astype(int)
