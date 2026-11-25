def _items_of_known_jobs(jobs, items):
    return int(items["job_id"].isin(jobs["job_id"]).sum())


def items_per_job(jobs, items):
    n_jobs = jobs["job_id"].nunique()
    return float(_items_of_known_jobs(jobs, items) / n_jobs) if n_jobs else None


def items_per_customer(jobs, items):
    n_customers = jobs["customer_id"].nunique()
    return float(_items_of_known_jobs(jobs, items) / n_customers) if n_customers else None
