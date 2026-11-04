## What a good answer contains

| # | pattern | the property that makes it work | time | trap |
|---|---|---|---|---|
| 1 | Kadane | one contiguous stretch, negatives allowed | O(n) | all days negative: start `best` at `a[0]` |
| 2 | prefix sums | static data, many range-sum queries | O(n + q) | updates between queries |
| 3 | two pointers | the list is sorted | O(n) | unsorted input |
| 4 | variable window | all values positive | O(n) | negative values: use prefix sums + monotonic deque |
| 5 | difference array | many range updates, one read at the end | O(n + q) | reads between updates |

## Rate yourself

For each scenario:

- 1 point for the right pattern;
- 1 point for naming the property that makes it valid (not just "it is fast");
- a half point for the cost comparison, a half point for a real trap.

8 or more out of 10 means you can choose the tool before you write code, which is the actual skill this module
teaches.
