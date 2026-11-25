import pandas as pd


def _ratio(num, den):
    return num / den if den else None


def completion_rates(jobs, start, end):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    cohort = jobs[(jobs["created_at"] >= start) & (jobs["created_at"] < end)]
    status = cohort["status"]
    completed = int((status == "completed").sum())
    created = len(cohort)
    started = int(cohort["started_at"].notna().sum())
    decided = int(status.isin(["completed", "cancelled", "failed"]).sum())
    return {
        "completed_per_created": _ratio(completed, created),
        "completed_per_started": _ratio(completed, started),
        "completed_per_decided": _ratio(completed, decided),
    }
