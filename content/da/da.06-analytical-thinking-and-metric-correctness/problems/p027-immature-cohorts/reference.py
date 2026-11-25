import pandas as pd


def mature_completion_rate(jobs, cut, min_age_days):
    cut = pd.Timestamp(cut)
    seen = jobs[jobs["created_at"] < cut]
    mature = seen[seen["created_at"] <= cut - pd.Timedelta(days=min_age_days)]
    naive = float(seen["status"].eq("completed").mean()) if len(seen) else None
    rate = float(mature["status"].eq("completed").mean()) if len(mature) else None
    return {"naive": naive, "mature": rate, "jobs": len(seen), "mature_jobs": len(mature)}
