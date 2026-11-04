## Hint 1

Sorted, the first array is `-4 -1 -1 0 1 2` at indices `0 1 2 3 4 5`. With `i = 0`, the best you can do is
`-4 + 1 + 2 = -1`, which is still below 0. So every step for `i = 0` is `l+1`. How many steps until `l` meets `r`?

## Hint 2

After a `found`, do this in order: `l += 1`, `r -= 1`, then the `skip l` loop, then the `skip r` loop. Each loop
first asks `l < r`. In the third call, after the first `found` you have `l = 2`, `r = 4`. Is `a[2] == a[1]`? Then
`l` becomes 3. Is `a[4] == a[5]`? Then `r` becomes 3.

## Hint 3

The `skip i` test compares `a[i]` with `a[i - 1]`, the value **to its left** in the sorted array. The loop runs
`i` from 0 to `n - 3`. Write the table:

```
for each i in 0..n-3:
    if a[i] == a[i-1] (and i > 0): line "skip i <i>", next i
    l = i + 1, r = n - 1
    while l < r: one line per comparison, then move
```
