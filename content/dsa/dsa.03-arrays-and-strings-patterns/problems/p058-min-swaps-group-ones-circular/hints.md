## Hint 1

At the end, all `m` ones sit in a block of size `m`. Fix one candidate block. How many swaps does it need, if it
already contains `w` ones? (Each zero inside must be swapped with a one outside.)

## Hint 2

So you want the window of size `m` with the **most** ones, and the window may wrap around the end. Slide it with an
index `i` that goes past `n - 1`, and read `a[i % n]`: entering value `a[i % n]`, leaving value `a[(i - m) % n]`.

## Hint 3

```
m = number of ones; if m == 0: print 0
window = ones in a[0..m-1]; best = window
for i in m .. n + m - 2:
    window += a[i % n] - a[(i - m) % n]
    best = max(best, window)
print m - best
```

The last window starts at `n - 1`, so it ends at `n + m - 2`.
