# Count the longest increasing subsequences

Write `count_lis(nums)` that returns **how many** longest strictly increasing subsequences `nums` has. Subsequences are counted by **positions**: two subsequences with the same values at different positions are different.

## Example

```python
>>> count_lis([1, 3, 5, 4, 7])      # 1,3,5,7 and 1,3,4,7
2
>>> count_lis([2, 2, 2, 2, 2])      # length 1, five single items
5
>>> count_lis([1, 2, 4, 3, 5, 4, 7, 2])
3
>>> count_lis([])
0
```

In the third example the LIS length is 5, and the three of them are `1,2,4,5,7`, `1,2,3,5,7` and `1,2,3,4,7`.

## Constraints

- `0 <= len(nums) <= 800`, integers.
- Time `O(n^2)`. Listing all subsequences is exponential. The count can be large; Python integers are exact.

## Think about

The `O(n^2)` LIS table (chapter section 13) keeps `f[i]`, the longest length ending at `i`. What second number per index would let you count? When `j` gives a **longer** length for `i`, what happens to the count; when it gives the **same** length, what happens?
