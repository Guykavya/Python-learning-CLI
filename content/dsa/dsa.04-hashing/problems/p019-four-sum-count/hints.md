## Hint 1

Four loops cost `n^4`. What if you split the four lists into two halves and handle each half separately?

## Hint 2

Count every sum `a + b` in a dictionary: `pair_count[s]` = how many `(i, j)` give `s`. Then for every `c + d`, add `pair_count.get(-(c + d), 0)`.

## Hint 3

```
pair_count = {}
for a in A:
    for b in B:
        pair_count[a + b] = pair_count.get(a + b, 0) + 1
ans = 0
for c in C:
    for d in D:
        ans += pair_count.get(-(c + d), 0)
```
