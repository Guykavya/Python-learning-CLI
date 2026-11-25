# Top-decile lift

Chapter section 8.3. The **top-decile lift** is the target rate among the 10% highest-scored rows divided by the overall rate: "how many times better than random is the top of our list?"

```python
import numpy as np


def top_decile_lift(y, score):
    order = np.argsort(-score, kind="stable")
    k = max(1, len(y) // 10)
    return float(np.mean(y[order][:k]) / np.mean(y)), k


y = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0])
score = np.array([0.40, 0.10, 0.22, 0.97, 0.95, 0.31, 0.05, 0.66, 0.12, 0.18,
                  0.27, 0.83, 0.09, 0.35, 0.14, 0.02, 0.58, 0.44, 0.07, 0.25])
lift, k = top_decile_lift(y, score)
top_rate = lift * y.mean()
print(f"rows in the top decile: {k}")
print(f"base rate: {y.mean():.3f}")
print(f"top-decile rate: {top_rate:.3f}")
print(f"lift: {lift:.2f}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

With 10 rows, `k` would be 1: the lift would be the label of the single highest-scored row divided by the base rate.

## After you answer

- The score with the third-highest value belongs to a positive row. Would the lift change if `k` were 3? To what?
