## Hint 1

Write the update `2 4 5` on an array of 6 zeros as "what changes compared with the left neighbour?". Position 2 is 5
more than position 1. Positions 3 and 4 are the same as their left neighbours. Position 5 is 5 less than position 4.
Which two cells of `d` record that?

## Hint 2

`d[l] += v` and `d[r + 1] -= v`. Make `d` of size `n + 2` so that `r + 1 = n + 1` is still a valid index.
After all updates, a running total over `d[1..n]` gives the amount added to each position.

## Hint 3

```
d = [0] * (n + 2)
for each update l r v:
    d[l] += v
    d[r + 1] -= v
run = 0
for i in 1..n:
    run += d[i]
    a[i - 1] += run
print a
```
