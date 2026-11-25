def orphans(jobs, customers):
    known = customers["customer_id"]
    jobs_without_customer = jobs.loc[~jobs["customer_id"].isin(known), "job_id"]
    customers_without_job = customers.loc[~known.isin(jobs["customer_id"]), "customer_id"]
    return {
        "jobs_without_customer": sorted(jobs_without_customer.tolist()),
        "customers_without_job": sorted(customers_without_job.tolist()),
    }
