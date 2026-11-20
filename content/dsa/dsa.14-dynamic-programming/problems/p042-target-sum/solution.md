## Approach

Turn the story into counting subsets (chapter section 12). The `+` numbers sum to `P`, the `-` numbers to `N`:

- `P - N = target`
- `P + N = total`

so `P = (total + target) / 2`. Each sign pattern is exactly one choice of the plus-group, so the answer is **the number of subsets with sum `P`**. If `total + target` is odd or `abs(target) > total`, no such `P` exists: return 0.

```python
def target_sum(nums, target):
    total = sum(nums)
    if abs(target) > total or (total + target) % 2:
        return 0
    plus = (total + target) // 2         # sum of the numbers marked '+'
    f = [0] * (plus + 1)
    f[0] = 1
    for x in nums:
        for s in range(plus, x - 1, -1):     # downwards: each number once
            f[s] += f[s - x]
    return f[plus]
```

Check `[1, 1, 1, 1, 1]`, target 3: total 5, `P = 4`. Choosing which four ones get `+` is 5 ways. Zeros need no special case: for `x = 0` the loop includes `s = 0` and every `f[s] += f[s]` doubles the count, because `+0` and `-0` are two choices.

Why `abs(target)`? For a negative target `total + target` can be negative, so `P < 0`; for `target > total`, `P > total`. Both mean "impossible".

## Complexity

`O(n * P)` time, `O(P)` space, with `P <= total`.

## Another way

A memoised recursion over `(index, running sum)`: `ways(i, s) = ways(i + 1, s + nums[i]) + ways(i + 1, s - nums[i])`, with `ways(n, s) = 1 if s == target else 0`. The running sum stays between `-total` and `total`, so there are `O(n * total)` states. It is the most direct translation of the story and a good brute-force oracle without the cache. You can also do the same thing bottom-up with a dictionary `{sum: count}` that you rebuild for each number.
