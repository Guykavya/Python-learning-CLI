## Hint 1

What does the object need to *know* to compute itself: which column, which statuses, which customers to skip? Which of those
are data (fields of the dataclass) and which are logic (inside `compute`)? How do you choose a column of `jobs` when you
only have its name as text?

## Hint 2

```text
@dataclass(frozen=True) class Metric: name, numerator, denominator, date_basis, exclusions=()
compute:
    basis = jobs[metric.date_basis]
    rows = jobs where basis >= start and basis < end and customer_id not in metric.exclusions
    num = how many rows have status in metric.numerator
    if denominator is None: return int(num)
    den = how many rows have status in metric.denominator
    return num / den, or None when den is 0
METRICS = {"jobs_completed": Metric(...), "completion_rate": Metric(...)}
```
