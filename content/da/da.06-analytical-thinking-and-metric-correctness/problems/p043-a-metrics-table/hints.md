## Hint 1

What are the two nested loops you need, and which one is the outer loop if the rows must be grouped by metric? What
does `spec.fn` return and where does each of its three values go in the row? Which values must be Timestamps when you
call `fn`, and what do you put in a row when the denominator is `None`?

## Hint 2

```text
rows = []
for spec in specs:
    for label, (start, end) in months.items():
        value, numerator, denominator = spec.fn(ctx, pd.Timestamp(start), pd.Timestamp(end))
        rows.append({"metric": spec.name, "month": label, "unit": spec.unit, "numerator": numerator,
                     "denominator": NaN if denominator is None else denominator, "value": value})
return pd.DataFrame(rows, columns=[the six column names])
```
