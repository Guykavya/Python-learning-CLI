from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Metric:
    name: str
    numerator: tuple          # statuses counted in the numerator
    denominator: object       # None for a count, or a tuple of statuses for a rate
    date_basis: str           # the timestamp column that puts a job in a period
    exclusions: tuple = ()    # customer ids that are never counted (test accounts)


def compute(metric, jobs, start, end):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    basis = jobs[metric.date_basis]
    rows = jobs[(basis >= start) & (basis < end) & ~jobs["customer_id"].isin(metric.exclusions)]
    num = int(rows["status"].isin(metric.numerator).sum())
    if metric.denominator is None:
        return num
    den = int(rows["status"].isin(metric.denominator).sum())
    return num / den if den else None


METRICS = {
    "jobs_completed": Metric("jobs_completed", ("completed",), None, "completed_at", (99,)),
    "completion_rate": Metric("completion_rate", ("completed",), ("completed", "cancelled", "failed"), "created_at", (99,)),
}
