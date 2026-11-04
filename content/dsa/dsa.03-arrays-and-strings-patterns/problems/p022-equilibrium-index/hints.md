## Hint 1

If you know the total of the whole array and the sum of everything to the left of `i`, can you get the sum
to the right of `i` without another loop?

## Hint 2

`right = total - left - a[i]`. After checking position `i`, the next position's left sum grows by `a[i]`.
Be careful about the order: check first, then add `a[i]` to `left`.

## Hint 3

```
total = sum(a); left = 0
for i in 0..n-1:
    if left == total - left - a[i]: print i + 1 and stop
    left += a[i]
print -1
```
