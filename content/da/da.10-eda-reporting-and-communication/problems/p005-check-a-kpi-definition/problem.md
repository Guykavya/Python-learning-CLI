# Check a KPI definition

Chapter sections 3.1 and 3.2. A KPI is only useful when it is **precisely defined**: what is counted, out of what, at which grain, who owns it, which direction is good and what kind of KPI it is.
Write `check_kpi(defn)` that returns a list of problems for a definition given as a dict (an empty list when it is fine).

Checks, in this order:

1. For each required field, in the order `name, numerator, grain, owner, direction, type, unit`: if it is missing or empty, add `missing field: <field>`.
2. If `type` is given but not one of `leading`, `lagging`, `guardrail`, `vanity`: add `unknown type: <type>`.
3. If `type` is `vanity`: add `vanity metric: no decision depends on it`.
4. If `direction` is given but not `up` or `down`: add `direction must be 'up' or 'down'`.
5. If `unit` is `%` and `denominator` is missing or empty: add `a percentage needs a denominator`.

## Example

```python
check_kpi({"name": "Monthly churn", "numerator": "opening actives whose last week is in the month",
           "denominator": "customers active in the first week", "grain": "month", "owner": "Head of Retention",
           "direction": "down", "type": "lagging", "unit": "%"})        # []
check_kpi({"name": "Sign-ups ever", "numerator": "sign-ups", "grain": "all time", "owner": "", "direction": "up",
           "type": "vanity", "unit": "count"})
# ['missing field: owner', 'vanity metric: no decision depends on it']
```
