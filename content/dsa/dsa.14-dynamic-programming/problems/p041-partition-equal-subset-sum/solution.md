## Approach

Two equal groups each sum to half the total. So an odd total is impossible, and for an even total the question becomes **subset sum** with target `S // 2` (chapter section 12): if one group reaches exactly half, the rest is the other half. This is the reduction the chapter calls "recognise the knapsack inside the story".

```python
def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    half = total // 2
    f = [False] * (half + 1)
    f[0] = True                          # the empty subset
    for x in nums:
        for s in range(half, x - 1, -1):     # downwards: each number once
            if f[s - x]:
                f[s] = True
    return f[half]
```

`f[s]` means "some subset of the numbers processed so far sums to `s`". When the number `x` arrives, every reachable `s - x` makes `s` reachable. The loop goes **downwards** so that `f[s - x]` is still the value from before `x` was added; upwards, `x` could be used again (`[1, 2, 5]` would wrongly reach 4 as `1 + 1 + 2`).

## Complexity

`O(n * S)` time and `O(S)` space, where `S` is the total. For 200 numbers up to 100, `S / 2 <= 10,000`: about two million steps.

## Another way

The bitset trick of chapter section 12: `bits = 1`, then `bits |= bits << x` for every `x`, and the answer is bit `half` of `bits`. Python does the shifting inside its big-integer code, so it is much faster. You can also stop early: once `f[half]` is `True`, return.

A memoised recursion `can(i, s)` ("can the numbers from index `i` on reach `s`?") with `functools.cache` also works; there are at most `n * (half + 1)` states. Without the cache it tries all `2**n` subsets.
