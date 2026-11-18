## Approach

The recipe of section 2:

- **State:** `f[i]` = the fewest jumps to arrive at index `i`.
- **Transition (push form):** from a reached index `i`, every `j` in `i + 1 .. i + nums[i]` can be reached with `f[i] + 1` jumps; keep the minimum at `j`.
- **Base:** `f[0] = 0`; every other cell starts at `INF`.
- **Answer:** `f[n - 1]`, or `-1` if it stayed `INF`.

Jumps only go to the right, so every index that can reach `j` lies to the left of `j`. When the loop reaches `i`, all of its senders have been processed and `f[i]` is final. That is the "iteration order" rule of section 4.

```python
INF = float("inf")


def min_jumps(nums):
    n = len(nums)
    f = [INF] * n            # f[i] = fewest jumps to arrive at index i
    f[0] = 0
    for i in range(n):
        if f[i] == INF:      # nobody reaches i, so i sends nothing forward
            continue
        for j in range(i + 1, min(n - 1, i + nums[i]) + 1):
            if f[i] + 1 < f[j]:
                f[j] = f[i] + 1
    return f[n - 1] if f[n - 1] != INF else -1
```

`INF` does the work of "impossible" in the arithmetic: `INF + 1` is still `INF` and never wins a `min` (section 7). The `continue` is only a shortcut.

## Complexity

`O(n * J)` time, where `J` is the largest jump, and `O(n)` space. The plain recursion that tries every jump is exponential: `[3] * 400` has more than `3^130` routes, but only 400 different states.

## Another way

The greedy of dsa.13 (jump game II) runs in `O(n)`: scan layers, and if `i` ever passes the farthest reachable index, return `-1`. It is faster, but needs a proof that "jump to the index that reaches farthest" is safe. The DP needs no proof: it tries every jump, and it still works if the problem changes so that greedy no longer applies, for example if every landing index had a cost and you wanted the cheapest route (then `f[j] = min(f[i] + cost[j])`).

A top-down version with `functools.cache` also passes: `best(i)` = fewest jumps from `i` to the end, `1 + min(best(j))`. Its recursion depth is at most `n`, so keep `n` below the recursion limit.
