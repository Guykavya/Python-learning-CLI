## Hint 1

Sort the values in your head: `[3, 1, 3, 2]` becomes `1, 2, 3, 3`, so the positions are 1, 2, 3, 4. The two 3s occupy positions 3 and 4. What does each method do with "positions 3 and 4"?

## Hint 2

```text
positions of the tied 3s : 3 and 4
average -> 3.5 for both          min -> 3 for both          max -> 4 for both
dense   -> counts distinct values: 1, 2, 3  -> the 3s get 3 (no gap)
first   -> the first 3 in the data gets 3, the second gets 4
```
Then write the ranks back in the **original order** of the Series, not in sorted order.
For `t = [30, 10, 30, 20, 10]` the sorted values are `10, 10, 20, 30, 30` (positions 1 to 5). With `ascending=False` the order of positions flips: the 30s take positions 1 and 2.
