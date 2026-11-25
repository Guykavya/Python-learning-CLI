def paid_per_customer(jobs, payments):
    """Return a frame indexed by customer_id with integer columns `quoted` and `paid`."""
    raise NotImplementedError("sum the payments per job first, then join to jobs, then group by customer")
