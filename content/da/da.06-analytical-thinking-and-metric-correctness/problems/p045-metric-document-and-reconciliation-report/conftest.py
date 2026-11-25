"""The inline QuickFix data of the project test (timestamps already in IST) and three metric definitions."""
from dataclasses import dataclass
from typing import Callable

import pandas as pd
import pytest


@dataclass(frozen=True)
class MetricSpec:
    name: str
    question: str
    unit: str
    date_basis: str
    includes: str
    excludes: str
    fn: Callable                # fn(ctx, start, end) -> (value, numerator, denominator)


# (job_id, status, created_at, started_at, completed_at, quote_total): one row per reason, for February 2025
JOBS = [
    (1, "completed", "2025-02-03 09:00:00", "2025-02-04 09:00:00", "2025-02-04 13:00:00", 2000),   # in both sets; deposit in Jan, balance in Feb, refund in Feb
    (2, "completed", "2025-01-30 09:00:00", "2025-02-01 00:00:00", "2025-02-01 04:00:00", 1000),   # started exactly at the start of Feb: C only (late)
    (3, "cancelled", "2025-02-05 09:00:00", None, None, 500),                                       # T only: cancelled; but 100 was paid
    (4, "failed", "2025-02-06 09:00:00", "2025-02-07 09:00:00", None, 400),                         # T only: failed
    (5, "completed", "2025-02-28 23:00:00", "2025-03-01 00:00:00", "2025-03-01 03:00:00", 1500),    # T only: started exactly at the end; deposit in the last second of Feb
    (6, "pending", "2025-02-20 09:00:00", None, None, 600),                                         # T only: pending; deposit of 200 in Feb
    (7, "pending", "2025-01-25 09:00:00", "2025-02-10 09:00:00", None, 700),                        # in neither T nor C (pending, started in Feb)
    (8, "completed", "2025-01-20 09:00:00", "2025-01-31 09:00:00", "2025-01-31 23:59:59", 3000),    # completed in January; balance of 1000 paid in Feb
    (9, "completed", "2025-02-10 09:00:00", "2025-02-12 09:00:00", "2025-02-12 15:00:00", 800),     # in both sets; never paid
    (10, "completed", "2025-02-18 09:00:00", "2025-02-20 09:00:00", "2025-02-20 12:00:00", 1500),   # in both sets; paid exactly at the end of Feb; refund in the last second of Feb
]
PAYMENTS = [
    (1, 1, "2025-01-28 09:00:00", 500), (2, 1, "2025-02-12 09:00:00", 1500), (3, 2, "2025-02-01 00:00:00", 1000),
    (4, 3, "2025-02-05 09:00:00", 100), (5, 5, "2025-02-28 23:59:59", 300), (6, 5, "2025-03-01 00:00:00", 1200),
    (7, 6, "2025-02-21 09:00:00", 200), (8, 8, "2025-01-15 09:00:00", 2000), (9, 8, "2025-02-03 09:00:00", 1000),
    (10, 10, "2025-03-01 00:00:00", 1500),
]
REFUNDS = [(1, 1, "2025-02-15 09:00:00", 250), (2, 10, "2025-02-28 23:59:59", 150)]


def make_tables():
    j = pd.DataFrame(JOBS, columns=["job_id", "status", "created_at", "started_at", "completed_at", "quote_total"])
    for c in ("created_at", "started_at", "completed_at"):
        j[c] = pd.to_datetime(j[c])
    p = pd.DataFrame(PAYMENTS, columns=["payment_id", "job_id", "paid_at", "amount"])
    p["paid_at"] = pd.to_datetime(p["paid_at"])
    r = pd.DataFrame(REFUNDS, columns=["refund_id", "job_id", "refunded_at", "amount"])
    r["refunded_at"] = pd.to_datetime(r["refunded_at"])
    return {"jobs": j, "pay": p, "ref": r}


def _between(s, a, b):
    return (s >= a) & (s < b)


def _created(ctx, s, e):
    n = int(_between(ctx["jobs"]["created_at"], s, e).sum())
    return n, n, None


def _rate(ctx, s, e):
    j = ctx["jobs"]
    cohort = j[_between(j["created_at"], s, e) & ~j["status"].eq("pending")]
    top = int(cohort["status"].eq("completed").sum())
    return top / len(cohort), top, len(cohort)


def _cash(ctx, s, e):
    v = int(ctx["pay"].loc[_between(ctx["pay"]["paid_at"], s, e), "amount"].sum())
    return v, v, None


@pytest.fixture
def tables():
    return make_tables()


@pytest.fixture
def specs():
    return [
        MetricSpec("jobs_created", "How much demand arrived?", "jobs", "created_at (IST)", "all statuses", "none", _created),
        MetricSpec("completion_rate", "Of the demand that was decided, how much was finished?", "share of jobs",
                   "created_at (IST), cohort", "jobs created in the month, completed / all but pending", "pending jobs (not decided yet)", _rate),
        MetricSpec("cash_collected", "How much money arrived?", "rupees", "paid_at (IST)", "all payments", "refunds are not subtracted", _cash),
    ]
