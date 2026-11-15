## Approach

Turn the sum around: instead of "for every subarray, its minimum", compute "for every element, how many subarrays it is the minimum of", times its value. The span in which `arr[i]` is the minimum is bounded by the previous smaller and next smaller elements, which two monotonic-stack passes find for all `i` in `O(n)`. Ties are broken by making one side strict and the other not, so each subarray is credited to exactly one position (its rightmost minimum).

## Code

```python
MOD = 10 ** 9 + 7


def sum_subarray_mins(arr):
    n = len(arr)
    prev = [-1] * n                    # previous strictly smaller
    stack = []
    for i in range(n):
        while stack and arr[stack[-1]] >= arr[i]:
            stack.pop()
        prev[i] = stack[-1] if stack else -1
        stack.append(i)

    nxt = [n] * n                      # next smaller or equal
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and arr[stack[-1]] > arr[i]:
            stack.pop()
        nxt[i] = stack[-1] if stack else n
        stack.append(i)

    total = 0
    for i in range(n):
        total += arr[i] * (i - prev[i]) * (nxt[i] - i)
    return total % MOD
```

## Complexity

`O(n)` time (two stack passes and one sum) and `O(n)` memory.

## Another way

A single pass with dynamic programming: let `dp[i]` be the sum of the minimums of all subarrays **ending** at `i`. If `p` is the previous strictly smaller index, then `dp[i] = dp[p] + arr[i] * (i - p)` (with `dp[-1] = 0`), because subarrays that reach past `p` have the same minimum as those ending at `p`, extended by one. The answer is `sum(dp)`. The previous-smaller index comes from the same stack.
