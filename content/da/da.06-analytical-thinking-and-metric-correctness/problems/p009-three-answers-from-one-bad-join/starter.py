def correct_totals(joined):
    """`joined` is jobs LEFT-joined to items (one row per line, a job without items has one row with line_no missing).
    Return {"jobs": ..., "job_value": ..., "items": ...} with the correct numbers."""
    raise NotImplementedError("count jobs with nunique, sum quote_total once per job, count only real line items")
