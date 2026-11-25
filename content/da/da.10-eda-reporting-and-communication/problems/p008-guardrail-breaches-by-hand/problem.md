# Guardrail breaches by hand

Chapter section 3.2. A **guardrail** is a KPI you refuse to hurt. Each has a limit: a **max** (churn must not go above 5.0%) or a **min** (on-time delivery must not go below 90%).
A value **exactly on the limit** is allowed.

```python
import pandas as pd

kpis = pd.DataFrame({
    "month": ["2024-08", "2024-09", "2024-10", "2024-11"],
    "churn_rate_pct": [4.2, 5.0, 6.1, 4.9],
    "on_time_pct": [92.0, 80.5, 90.0, 89.9],
})
limits = {"churn_rate_pct": ("max", 5.0), "on_time_pct": ("min", 90.0)}


def guardrail_breaches(kpis, limits):
    out = []
    for _, row in kpis.iterrows():
        for kpi, (kind, limit) in limits.items():
            v = row[kpi]
            bad = v > limit if kind == "max" else v < limit
            if bad:
                out.append((row["month"], kpi, v))
    return out


for month, kpi, v in guardrail_breaches(kpis, limits):
    print(month, kpi, v)
print(len(guardrail_breaches(kpis, limits)))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

If December had churn 5.5 and on-time 95.0, it would add the line `2024-12 churn_rate_pct 5.5`.

## After you answer

- Which two values sit exactly on a limit, and why are they not breaches?
- Inside one month, which KPI is checked first?
