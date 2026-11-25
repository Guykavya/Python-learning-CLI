# Cash against work

Chapter section 14.5. Finance asks: "February completed work is worth X, but February cash is Y. Where is the
difference?" The answer is in the payment records. Every rupee of completed work and every rupee of cash goes into a
named bucket, and the buckets add up to the difference.

Write `cash_vs_work(jobs, payments, refunds, start, end)` for the half-open period `[start, end)` (Timestamps or texts).

Tables:

- `jobs`: `job_id`, `status`, `completed_at` (`NaT` when not completed), `quote_total`
- `payments`: `payment_id`, `job_id`, `paid_at`, `amount`
- `refunds`: `refund_id`, `job_id`, `refunded_at`, `amount`

Definitions:

- **work value** = `quote_total` summed over jobs with status `completed` and `completed_at` in the period.
- **cash gross** = payments with `paid_at` in the period. **refunds** = refunds with `refunded_at` in the period.
  **net cash** = cash gross - refunds.

Return a dict with `"work_value"`, `"cash_gross"`, `"refunds"`, `"net_cash"` (plain ints) and

- `"steps"`: **always these seven** `(label, amount)` pairs, in this order, signed so that
  `work_value + sum(amounts) == net_cash`. Take **all** payments of the jobs completed in the period
  (`before`: `paid_at < start`, `inside`: in the period, `after`: `paid_at >= end`):
  1. `"completed in month, paid before the month"`: `-(sum of before)`
  2. `"completed in month, paid after the month"`: `-(sum of after)`
  3. `"completed in month, not paid yet"`: `-(work_value - before - inside - after)`
  4. `"paid in month, job completed earlier"`: `+` payments inside the period on jobs **not** completed in it
     whose `completed_at < start`
  5. `"paid in month, job completed later or pending"`: `+` such payments on jobs with `completed_at >= end`, or status `pending`
  6. `"paid in month, other jobs"`: `+` all remaining such payments (cancelled or failed jobs, unknown jobs)
  7. `"refunds issued in month"`: `-refunds`
- `"ids"`: a dict from each of the seven labels to the **sorted list of job ids** behind that line (empty list when
  the amount is zero or no job is involved). For line 3: the jobs completed in the period whose payments (all dates) add up to
  **less than** their `quote_total`. For lines 1 and 2: the jobs with a payment before / after. For lines 4-6: the jobs of those payments.
  For line 7: the jobs of the refunds in the period.
- `"closes"`: `True` when `work_value + sum(step amounts) == net_cash`

Do not change the inputs.

## Example

```python
import pandas as pd

jobs = pd.DataFrame({"job_id": [1, 2], "status": ["completed", "completed"],
                     "completed_at": pd.to_datetime(["2025-02-10 09:00", "2025-02-20 09:00"]), "quote_total": [1000, 500]})
pay = pd.DataFrame({"payment_id": [1, 2], "job_id": [1, 1], "paid_at": pd.to_datetime(["2025-01-28 09:00", "2025-02-12 09:00"]),
                    "amount": [300, 700]})
ref = pd.DataFrame({"refund_id": [], "job_id": [], "refunded_at": pd.to_datetime([]), "amount": []})
r = cash_vs_work(jobs, pay, ref, "2025-02-01", "2025-03-01")
print(r["work_value"], r["cash_gross"], r["net_cash"], r["closes"])
for label, amount in r["steps"]:
    print(f"{amount:+6d}  {label}")
```

```text
1500 700 700 True
  -300  completed in month, paid before the month
    +0  completed in month, paid after the month
  -500  completed in month, not paid yet
    +0  paid in month, job completed earlier
    +0  paid in month, job completed later or pending
    +0  paid in month, other jobs
    +0  refunds issued in month
```
