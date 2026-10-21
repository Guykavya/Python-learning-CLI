## Hint 1

There are four kinds of year: divisible by 400, divisible by 100 (but not 400), divisible by 4 (but not 100), and the rest. What answer does each kind get?

## Hint 2

Check the most specific rule first. With `if / elif / else`: test `% 400` first, then `% 100`, then `% 4`. Or write the rule as one condition using `and` / `or`.

## Hint 3

```
if year % 400 == 0: leap
elif year % 100 == 0: not leap
elif year % 4 == 0: leap
else: not leap
```
