## Hint 1

Work class by class. How do you get the positions of one class in `y`? How do you pick some of them at random, with the same generator for every class?

## Hint 2

```text
rng = default_rng(seed); test = []
for c in sorted(unique(y)):
    pos = where(y == c)[0]; m = len(pos)
    k = round(test_frac * m); if m >= 2: k = min(max(k, 1), m - 1) else k = 0
    test.extend(rng.choice(pos, size=k, replace=False))
test_idx = sort(test); train_idx = the rest, sorted
```
