## Approach

Chapter section 7, "Counting the ways (sequences, order matters)". Let `f[a]` be the number of sequences that sum to exactly `a`.

- **Transition:** split on the **last** number `x` of the sequence. What is in front of it is any sequence summing to `a - x`. Different last numbers give different sequences, so the counts add: `f[a] = sum(f[a - x] for x in nums if x <= a)`.
- **Base:** `f[0] = 1`, the empty sequence. Without it nothing can ever be counted.
- **Order:** `f[a]` reads smaller amounts, and those must already be final, so the amount loop is outside and goes up.

```python
def ordered_ways(nums, target):
    f = [0] * (target + 1)
    f[0] = 1                         # the empty sequence
    for a in range(1, target + 1):   # outer loop: amounts
        for x in nums:               # inner loop: the last number of the sequence
            if x <= a:
                f[a] += f[a - x]
    return f[target]
```

For `[1, 2, 3]` the table is:

| a | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| f[a] | 1 | 1 | 2 | 4 | 7 |

`f[4] = f[3] + f[2] + f[1] = 4 + 2 + 1 = 7`.

## Why p018 gives a different answer

| Outer loop | Inner loop | When `f[a]` is read, it uses | Counts |
|---|---|---|---|
| numbers | amounts | only the numbers seen so far | combinations (p018) |
| amounts | numbers | every number | sequences (this problem) |

With the numbers outside, a sequence can only be built "all 1s, then all 2s, then all 3s", so `2 + 1 + 1` is never built separately from `1 + 1 + 2`. With the amounts outside, the last number can be anything at every step, so every order appears.

## Complexity

`O(target * len(nums))` time, `O(target)` space. The counts grow very fast (for `[1, 2]` they are the Fibonacci numbers), so Python's big integers matter: in a fixed-size language this problem needs a modulus.

## Another way

Top-down with a memo: `ways(a) = 1 if a == 0 else sum(ways(a - x) for x in nums if x <= a)`, wrapped in `functools.cache`. It is the same recurrence, but for `target = 10**4` with `nums = [1]` the recursion is 10,000 calls deep and passes Python's default limit (chapter section 3, "The traps of memoisation"). The table has no depth problem.
