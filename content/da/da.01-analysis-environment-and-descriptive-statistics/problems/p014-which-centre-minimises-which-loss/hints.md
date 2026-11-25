## Hint 1

Write `total_loss` first and check it by hand on `[1, 2, 6]`. For `best_centre`, which numbers are you allowed to try, and how do you choose the best of them with `min`?

## Hint 2

```text
candidates = set(values) | {mean}
best = min(sorted(candidates), key=lambda c: total_loss(values, c, kind))
```
`min` returns the first smallest item, so sorting the candidates first makes ties go to the smaller number.
