# Find the records behind the gap

Chapter section 11.2. "The dashboard says 4,200, the ledger says 2,700" is where a reconciliation **starts**. The
outcome is a list of records and a reason for each one. A number is a sum over records, so the difference between two
numbers is a sum over the records that differ.

Write `explain_gap(dashboard, sql_result)`.

- Both arguments are DataFrames with the columns `job_id` and `amount` (several rows per job are possible; the
  dashboard may repeat rows because of a join that fans out).
- Per job, add up the amounts on each side. The **contribution** of a job is
  `dashboard sum - sql sum` (a job missing on one side counts as 0 there).
- Return a dict with:
  - `"gap"`: `dashboard["amount"].sum() - sql_result["amount"].sum()`
  - `"by_job"`: `{job_id: contribution}` for every job whose contribution is **not zero**, ordered by `job_id`
  - `"reasons"`: `{job_id: label}` for the same jobs, where the label is
    - `"only in dashboard"` when the job is missing from `sql_result`
    - `"only in sql result"` when the job is missing from `dashboard`
    - `"repeated rows: D rows in dashboard, S rows in sql result"` when both have it but with a different number of rows
    - `"amount differs"` when both have it with the same number of rows
  - `"unexplained"`: `gap - sum(by_job.values())`, which must be `0`
- Job ids and amounts are plain Python ints in the result. Do not change the inputs.

## Example

```python
import pandas as pd

dash = pd.DataFrame({"job_id": [1, 1, 2], "amount": [500, 500, 300]})     # job 1 appears twice
sql = pd.DataFrame({"job_id": [1, 2], "amount": [500, 300]})
r = explain_gap(dash, sql)
print(r["gap"], r["by_job"], r["unexplained"])
print(r["reasons"])
```

```text
500 {1: 500} 0
{1: 'repeated rows: 2 rows in dashboard, 1 rows in sql result'}
```
