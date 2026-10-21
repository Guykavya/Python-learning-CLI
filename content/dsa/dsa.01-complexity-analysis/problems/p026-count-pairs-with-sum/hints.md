## Hint 1

With `n = 2 * 10^5`, all pairs means 2 * 10^10 checks: far too slow. And when all values are equal the answer itself is
about 2 * 10^10, so you cannot even find the pairs one at a time. You must count them in groups.

## Hint 2

Scan left to right. Standing at `a[j]`, the number of pairs ending at `j` is the number of **earlier** positions that
hold `t - a[j]`. Keep a dict from value to how many times it has appeared so far.

## Hint 3

```
seen_count = empty dict
pairs = 0
for x in a:
    pairs += seen_count of (t - x), or 0 if absent
    increase seen_count of x by 1
```
Look up first, then add `x`, so `x` never pairs with itself.
