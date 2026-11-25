import pandas as pd

FEB_START = pd.Timestamp("2025-02-01")
FEB_END = pd.Timestamp("2025-03-01")
IST = pd.Timedelta(hours=5, minutes=30)


def _in_feb(s):
    return (s >= FEB_START) & (s < FEB_END)


def completed_in_february(jobs, definition):
    done = jobs["status"].eq("completed")
    if definition == "by_created":
        mask = _in_feb(jobs["created_at"])
    elif definition == "by_started":
        mask = _in_feb(jobs["started_at"])
    elif definition == "by_completed":
        mask = done & _in_feb(jobs["completed_at"])
    elif definition == "by_completed_ist":
        mask = done & _in_feb(jobs["completed_at"] + IST)
    else:
        raise ValueError(f"unknown definition: {definition!r}")
    return int(mask.sum())
