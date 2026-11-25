## Hint 1

You need to look at every pair of two different colours exactly once. Which loop (or `itertools` function) gives pairs in the order `i < j`? Which of the two separation values do you compare with `min_sep`?

## Hint 2

```text
for i in range(len(palette)):
    for j in range(i + 1, len(palette)):
        if separation(palette[i], palette[j]) >= min_sep: keep (palette[i], palette[j])
```
