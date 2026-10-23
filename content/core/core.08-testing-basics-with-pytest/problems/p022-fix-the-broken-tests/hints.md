## Hint 1

Run the file against the correct `median` first (save the function as `target.py`). Which test fails, and is the function or the test wrong?

## Hint 2

Then read the file once more for the silent faults: what does `assert (a == b, "msg")` check? Which test has no `assert`? Which `def` names does pytest ignore, and what happens when two functions share a name?

## Hint 3

```
1. test_median_even: the answer for [1,2,3,4] is 2.5
2. the two test_median_odd: rename one
3. test_single: remove the parentheses around the assert
4. test_unsorted: add `assert ... == 4`
5. test_empty: only median([]) inside the with
6. tset_negative -> test_negative
```
