## Hint 1

Does the order in which you take the cards matter, or only **how many** you take from each end? After taking `x` from
the left and `k - x` from the right, which cards are still on the table? Are they consecutive?

## Hint 2

Maximising what you take = minimising what you leave. What you leave is a block of exactly `n - k` consecutive cards.
Find the smallest such block with a fixed-size sliding window, and subtract it from the total.

## Hint 3

```
keep = n - k
window = sum(a[0:keep])           # 0 when keep = 0
smallest = window
for i in keep..n-1:
    window += a[i] - a[i - keep]
    smallest = min(smallest, window)
print sum(a) - smallest
```
