# Metric document and reconciliation report

**Project.** Chapter section 14. The management of QuickFix argue every month about the numbers. You write the two
documents that end the arguments, and **both are produced by code**, so that the documents cannot disagree with the numbers.
The company reports in **IST**; the tables you receive already have their timestamps in IST.

You may reuse everything you wrote in this module: the `bridge` of problem 38, the volume bridge of problem 39 and the cash
bridge of problem 44. The test supplies the data and the metric objects (in a `conftest.py` you do not get when you start; the
interface is described here, the test file shows the data).

## Part 1. `definition_doc(specs)`

`specs` is a list of objects with the attributes `name`, `question`, `unit`, `date_basis`, `includes`, `excludes` (all
text; there is also `fn`, which you do not need here). Each one looks like this:

```python
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class MetricSpec:
    name: str
    question: str
    unit: str
    date_basis: str
    includes: str
    excludes: str
    fn: Callable            # fn(ctx, start, end) -> (value, numerator, denominator)
```

Return **one text** made of these lines joined with `"\n"`:

```text
# QuickFix: metric definitions (v1)

All dates are IST (UTC+05:30). A month is a half-open interval [first day, first day of next month).

```

then, for **each spec in order**, these seven lines (the last one is empty):

```text
### <name>
- Question: <question>
- Unit: <unit>
- Date basis: <date_basis>
- Includes: <includes>
- Excludes: <excludes>

```

So the text ends with `"\n"` (after the last `Excludes` line comes the empty line, then nothing).

## Part 2. `reconciliation_report(tables, month)`

`tables` is a dict with three DataFrames (IST timestamps): `"jobs"` (`job_id`, `status`, `created_at`, `started_at`,
`completed_at`, `quote_total`), `"pay"` (`payment_id`, `job_id`, `paid_at`, `amount`) and `"ref"` (`refund_id`, `job_id`,
`refunded_at`, `amount`). `month` is a pair of texts `(start, end)`, a half-open period.

Return one text (lines joined with `"\n"`, no newline at the end) with this layout; the bridge tables use the format of
problem 38 (lines right-stripped):

```text
# Reconciliation report: <start> to <end> (IST)

## 1. Total volume against completed volume

<bridge table>

Jobs behind each line:
- <step label>: <sorted list of job ids>
...

## 2. Completed work against net cash

<bridge table>

Jobs behind each line:
- <step label>: <sorted list of job ids>
...
```

- **Bridge 1** goes from `total volume (created in month)` (jobs created in the period) to
  `completed volume (started in month)` (jobs with status `completed` that started in the period), with the steps of
  problem 39: the labels `created in month, cancelled (never started)`, `created in month, failed`,
  `created in month, pending (no start date yet)`, `created in month, started after the month` (sorted by label, each
  negative) and last `created before the month, started in it` (positive). **Lines with no job are left out.**
- **Bridge 2** goes from `completed value (month)` to `net cash (month)` with the **seven** lines of problem 44 (all seven,
  also when zero).
- Under each bridge, `Jobs behind each line:` lists, in the order of the bridge, one line `- <label>: [ids]` for each step
  that has jobs. If no step has jobs, the single line `- none`.
- Both bridges must **close**: use the check of problem 38 (the last line ends with `OK`); a bridge that does not close is
  a bug, so raise `ValueError` as problem 38 does.

Do not change the tables.

## What the test checks

- The document has a header and **every metric section has all six fields**, in order.
- The report for February matches a hand-counted text exactly (every boundary timestamp in the data is there on purpose:
  start included, end excluded).
- For other months (March, a month with no data) both bridges still close and every running total is the previous one
  plus the change.

## Example

```python
print(definition_doc([MetricSpec("jobs_created", "How much demand arrived?", "jobs", "created_at (IST)", "all statuses", "none", None)]))
```

```text
# QuickFix: metric definitions (v1)

All dates are IST (UTC+05:30). A month is a half-open interval [first day, first day of next month).

### jobs_created
- Question: How much demand arrived?
- Unit: jobs
- Date basis: created_at (IST)
- Includes: all statuses
- Excludes: none

```
