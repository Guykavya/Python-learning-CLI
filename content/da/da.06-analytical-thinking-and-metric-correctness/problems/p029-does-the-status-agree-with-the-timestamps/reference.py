LABELS = [
    "completed without completed_at",
    "completed_at on a non-completed job",
    "cancelled without cancelled_at",
    "cancelled but started",
    "completed before it started",
    "started before it was created",
]


def lifecycle_problems(jobs):
    j = jobs
    masks = [
        j["status"].eq("completed") & j["completed_at"].isna(),
        j["status"].ne("completed") & j["completed_at"].notna(),
        j["status"].eq("cancelled") & j["cancelled_at"].isna(),
        j["status"].eq("cancelled") & j["started_at"].notna(),
        j["completed_at"] < j["started_at"],
        j["started_at"] < j["created_at"],
    ]
    found = []
    for order, (label, mask) in enumerate(zip(LABELS, masks)):
        for job_id in j.loc[mask, "job_id"]:
            found.append((int(job_id), order, label))
    found.sort()
    return [(job_id, label) for job_id, _, label in found]
