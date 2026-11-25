# Re-run for any date

Chapter section 7.2. A report that can be rebuilt **as of any date** is a monitor: run it every month and it tells you when something moves. It must use **only what was known on that date**.

`monthly_kpis(customers, panel)` is given in `starter.py` (section 3.4). Write `quick_summary(customers, panel, as_of)`:

1. keep only panel rows with `week <= as_of`;
2. a customer's `last_week` that is **after** `as_of` was not known yet: treat it as `NaT` (still active);
3. the last **complete** month is the month before the month of `as_of`; drop every month after it (a half month would show a false low or high);
4. return a dict:
   `{"as_of": "YYYY-MM-DD", "last_month": "YYYY-MM", "months": <number of months in the table>, "opening_last": <int>, "churn_last": <float>, "on_time_last": <float>}`
   where the `_last` values are those of the last complete month.

The test adds **future rows** (later weeks, later departures, new customers after `as_of`): the result must not change.

## Example

`as_of = "2024-02-14"`: the last complete month is January 2024, even if the panel has rows up to the end of February.
