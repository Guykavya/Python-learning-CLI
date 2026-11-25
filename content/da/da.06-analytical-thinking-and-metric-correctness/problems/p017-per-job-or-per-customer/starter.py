def items_per_job(jobs, items):
    """Line items per job (jobs without lines count as jobs)."""
    raise NotImplementedError("number of line items of known jobs divided by the number of jobs")


def items_per_customer(jobs, items):
    """Line items per customer who has at least one job."""
    raise NotImplementedError("the same numerator, divided by the number of distinct customers")
