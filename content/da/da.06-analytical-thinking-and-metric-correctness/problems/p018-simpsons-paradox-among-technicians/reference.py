def _rates(df, by):
    done = df["status"].eq("completed")
    grouped = done.groupby(df[by]).mean()
    return {k: float(v) for k, v in grouped.items()}


def completion_by_tech(jobs):
    by_type = {}
    for job_type, part in jobs.groupby("job_type"):
        by_type[job_type] = _rates(part, "tech")
    return {"overall": _rates(jobs, "tech"), "by_type": by_type}


def paradox(jobs, a, b):
    out = completion_by_tech(jobs)
    shared = [t for t, rates in out["by_type"].items() if a in rates and b in rates]
    if not shared:
        return False
    a_wins_everywhere = all(out["by_type"][t][a] > out["by_type"][t][b] for t in shared)
    a_loses_overall = out["overall"][a] < out["overall"][b]
    return bool(a_wins_everywhere and a_loses_overall)
