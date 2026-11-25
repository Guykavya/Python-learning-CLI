# Pooled retention curve

Chapter section 4.3. To give one number per month since the first order ("what share is still buying in month 3?"), pool the cohorts. Two rules make it correct:

1. use only the cohorts that **have reached** month `k` (their cell is not `NaN`);
2. **weight by cohort size**: add up the active customers and divide by the sum of the sizes of those cohorts. An average of the cohort *rates* would give a tiny cohort the same say as a huge one.

Write `pooled_retention(active, sizes, ks)`:

- `active`: DataFrame, rows = cohorts, columns = `k`, values = **number** of active customers (`NaN` where not yet observed);
- `sizes`: Series of cohort sizes with the same index as `active`;
- `ks`: the months to report. Return a Series indexed by `ks` with the pooled retention as a **proportion**; `NaN` when no cohort has reached that `k` (or the column does not exist).

## Example

Cohorts of 100, 10 and 50 customers with 50, 8 and `NaN` active in month 1: the pooled value is `(50 + 8) / (100 + 10) = 0.527`, not the average of the rates `(0.5 + 0.8) / 2 = 0.65`.
