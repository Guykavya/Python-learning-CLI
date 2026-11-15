## Hint 1

You don't need to choose which zeros to flip. A subarray can become all ones exactly when it contains at most
`k` zeros. So the question is: what is the longest window with at most `k` zeros?

## Hint 2

Grow the window with `r` and count the zeros inside it. When the count goes above `k`, move `l` right until it is
`k` again, decreasing the count whenever a zero leaves. After that the window is valid: compare `r - l + 1` with
the best.

## Hint 3

```
l = 0; zeros = 0; best = 0
for r in 0..n-1:
    if a[r] == 0: zeros += 1
    while zeros > k:
        if a[l] == 0: zeros -= 1
        l += 1
    best = max(best, r - l + 1)
print best
```
