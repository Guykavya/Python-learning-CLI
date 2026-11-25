## Hint 1

For `s`, which values does pandas use by default for `sum`, `mean` and `count`? (It skips the missing one.) For `e`, there is nothing to use: what is the sum of an empty list, and what is `0 / 0`? Remember that every comparison with `nan` is False.

## Hint 2

```text
s = [1, nan, 3]    sum = 1+3 = 4.0     mean = 4/2 = 2.0     count = 2
                   sum(min_count=1)    4.0 (at least one real value)
                   sum(skipna=False)   nan (one nan poisons the sum)
e = [nan]          sum = 0.0 (nothing to add)   sum(min_count=1) = nan (needs 1 value)
                   mean = nan (0 / 0)           count = 0
nan == nan         False       (s == nan) -> all False       isna -> [False, True, False]
```
