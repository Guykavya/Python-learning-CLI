## Hint 1

`np.select(conditions, choices, default)` takes the **first** true condition for each element. In which order must you list the conditions so that 95 becomes `"A"` and not `"D"`? And what does `nan >= 40` give, so where would a `nan` end up?

## Hint 2

```text
s = np.asarray(scores, dtype=float)
conditions = [isnan(s), s >= 90, s >= 75, s >= 60, s >= 40]
choices    = ["missing", "A", "B", "C", "D"]
return np.select(conditions, choices, default="F")
```
