def correct_totals(joined):
    per_job = joined.drop_duplicates(subset=["job_id"])
    return {
        "jobs": int(joined["job_id"].nunique()),
        "job_value": int(per_job["quote_total"].sum()),
        "items": int(joined["line_no"].count()),
    }
