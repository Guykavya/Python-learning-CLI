## Hint 1

Which of `len`, `count()` and `nunique()` skips missing values? Which one counts a repeated value only once? Match each of
the three questions to one of them.

## Hint 2

```text
rows               = len(payments)
with_method        = count of the method column (non-missing)
distinct_customers = nunique of the customer_id column
wrap each in int(...)
```
