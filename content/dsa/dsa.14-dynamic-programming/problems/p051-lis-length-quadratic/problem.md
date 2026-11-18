# LIS length in O(n^2)

A **subsequence** keeps the order of the list but may skip items. Write `lis_length(nums)` that returns the length of the longest **strictly increasing** subsequence (chapter section 13, "The `O(n^2)` DP").

## Example

```python
>>> lis_length([10, 9, 2, 5, 3, 7, 101, 18])    # for example 2, 3, 7, 18
4
>>> lis_length([0, 1, 0, 3, 2, 3])              # 0, 1, 2, 3
4
>>> lis_length([7, 7, 7, 7])                    # strictly: equal values do not count
1
>>> lis_length([])
0
```

## Constraints

- `0 <= len(nums) <= 800`, values are integers (negative allowed).
- Time `O(n^2)`. Trying every subsequence (`2**n`) does not finish.

## Think about

"The LIS of the first `i` items" is a natural state, but it has no simple transition: to extend it you need to know its **last value**. Which state, chosen by its end point, fixes that (chapter section 13)? Why is the answer `max(f)` and not `f[-1]`?
