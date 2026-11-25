# Fix the lying report

Chapters 6 and 7. `build_report(R)` in `starter.py` was copied from last quarter's report and edited under time pressure. It **looks** fine on the current data, but:

1. **two numbers are typed by hand** instead of taken from `R` (one in the headline, one in the impact);
2. the evidence rounds the **interval** to two decimals while the **estimate** has one (`2.9 (95% CI 2.71 to 3.09)`): the same rule must apply to both;
3. when there are **more than three limitations**, the extra ones are **silently dropped**.

Fix it. After your fix, for any `R`:

- the headline contains `{churn_before:.1f}%` and `{churn_after:.1f}%`;
- the impact contains `about {saved:.0f} customers (range {saved_lo:.0f} to {saved_hi:.0f})`;
- the first evidence item is exactly
  `Customers with a recent late box leave {rr:.1f} times as often (95% CI {rr_lo:.1f} to {rr_hi:.1f}).`;
- `limitations` equals `R["limitations"]` (all of them, in order);
- `lint_finding` (conftest, chapter section 6.4) finds no issue.

Keep the `Finding` class as it is.

## Example

With `churn_before = 3.21`, the headline must say `3.2%`; the current code says `4.0%` whatever the data.
