# Which centre minimises which loss?

Chapter sections 8 and 10. A "centre" is the single number `c` that stands for the whole list. Two ways of measuring how badly `c` represents the data:

- **squared loss**: `sum((x - c) ** 2 for x in values)`; its minimum is at the **mean**;
- **absolute loss**: `sum(abs(x - c) for x in values)`; its minimum is at the **median** (any point between the two middle values when the count is even).

Write:

- `total_loss(values, c, kind)` where `kind` is `"squared"` or `"absolute"`; any other `kind` raises `ValueError`.
- `best_centre(values, kind)`: search these **candidate points**: every value in the data **and** the mean of the data. Return the candidate with the smallest loss (on a tie, the smaller number). Empty `values` raises `ValueError`.

## Example

```python
total_loss([1, 2, 6], 3, "squared")    # 4 + 1 + 9 = 14
total_loss([1, 2, 6], 2, "absolute")   # 1 + 0 + 4 = 5
best_centre([1, 2, 6], "squared")      # 3.0  (the mean)
best_centre([1, 2, 6], "absolute")     # 2    (the median)
```
