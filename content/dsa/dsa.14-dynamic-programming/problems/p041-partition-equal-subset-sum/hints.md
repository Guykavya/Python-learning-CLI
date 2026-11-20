## Hint 1

Let `S = sum(nums)`. If the two groups are equal, each one sums to `S / 2`. So: when `S` is odd, the answer is `False` at once. When `S` is even, the question is only "is there a subset with sum `S // 2`?" The second group is everything else, and it sums to `S // 2` automatically.

## Hint 2

That is subset sum. Keep a list `f` of booleans, `f[s]` = "some subset of the numbers seen so far sums to `s`". Start with only `f[0] = True` (the empty subset). Which way must the `s` loop run so that a number is not used twice?

## Hint 3

```
S = sum(nums)
if S is odd: return False
half = S // 2
f = [False] * (half + 1); f[0] = True
for x in nums:
    for s from half down to x:
        if f[s - x]: f[s] = True
return f[half]
```
