import pandas as pd
from solution import completion_by_tech, paradox

rows = ([("A", "easy", "completed")] + [("A", "hard", "completed")] + [("A", "hard", "failed")] * 3
        + [("B", "easy", "completed")] * 3 + [("B", "easy", "failed")] + [("B", "hard", "failed")])
jobs = pd.DataFrame(rows, columns=["tech", "job_type", "status"])
jobs.insert(0, "job_id", range(1, len(jobs) + 1))
print(completion_by_tech(jobs))
print(paradox(jobs, "A", "B"), paradox(jobs, "B", "A"))
