## Hint 1

Normalise a **copy** of each table first (index and columns). Then compare the sets of labels, then loop over the labels both tables share.

## Hint 2

```text
norm(l) = "grand total" if str(l).strip().lower() in ("total", "grand total") else str(l).strip().lower()
only_exp = sorted(set(exp.index) - set(got.index)); ...
for r in exp.index (if in both): for c in exp.columns (if in both): if abs(e - g) > tol: message
```
