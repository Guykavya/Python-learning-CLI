# Best threshold from a cost curve

Chapter section 10. Choose the decision threshold that **minimises the total cost** on a **validation** set (never on the test set: the threshold is a tuned parameter).

Write `best_threshold(y_val, p_val, cost, grid)`:

- `cost` is a dict with any of the keys `"tn"`, `"fp"`, `"fn"`, `"tp"` (a missing key costs 0)
- for every threshold `t` in `grid`, predict positive when `p_val >= t`, count TN, FP, FN, TP and compute the total cost
- return the threshold with the **lowest** total cost (the first one in `grid` on a tie), as a float

The function has exactly these four parameters: it cannot see the test data.

## Example

```text
y_val = [1,0,0,1,0,0,0,1,0,0];  p_val = [0.9,0.6,0.4,0.35,0.2,0.55,0.1,0.65,0.3,0.8]
best_threshold(y_val, p_val, {"fp": 5, "fn": 100}, [0.3, 0.5, 0.7])   ->  0.3
```
For calibrated probabilities the best threshold is close to `cost_fp / (cost_fp + cost_fn)` (with no cost for TN and TP).
