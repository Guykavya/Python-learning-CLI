import pandas as pd


def volume_bridge(jobs, start, end):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    created = (jobs["created_at"] >= start) & (jobs["created_at"] < end)
    started = (jobs["started_at"] >= start) & (jobs["started_at"] < end)
    in_t = created
    in_c = started & jobs["status"].eq("completed")
    in_p = started & jobs["status"].eq("pending")
    ids = lambda m: {int(j) for j in jobs.loc[m, "job_id"]}
    t_only = jobs[in_t & ~in_c]
    c_only = jobs[in_c & ~in_t]
    names = {"cancelled": "cancelled (never started)", "failed": "failed", "pending": "pending (no start date yet)"}
    reasons = {int(r.job_id): names.get(r.status, "started after the month") for r in t_only.itertuples()}
    reasons.update({int(j): "created before the month, started in it" for j in c_only["job_id"]})
    counts = {}
    for job_id, label in reasons.items():
        counts[label] = counts.get(label, 0) + 1
    late = "created before the month, started in it"
    steps = [(f"created in month, {label}", -n) for label, n in sorted(counts.items()) if label != late]
    if late in counts:
        steps.append((late, counts[late]))
    closes = int(in_t.sum()) + sum(change for _, change in steps) == int(in_c.sum())
    return {"T": ids(in_t), "C": ids(in_c), "P": ids(in_p), "reasons": reasons, "steps": steps, "closes": closes}
