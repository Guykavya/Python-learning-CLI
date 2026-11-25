import pandas as pd

IST = pd.Timedelta(hours=5, minutes=30)


def jobs_per_ist_day(jobs):
    local = jobs["created_at"] + IST
    counts = local.dt.strftime("%Y-%m-%d").value_counts().sort_index()
    return {day: int(n) for day, n in counts.items()}
