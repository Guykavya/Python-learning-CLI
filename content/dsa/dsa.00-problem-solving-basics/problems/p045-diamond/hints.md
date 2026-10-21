## Hint 1

For `n = 3`, the rows have 1, 3, 5, 3, 1 stars. The top half is exactly the pyramid. For the bottom half, which
values of `i` would give 3 stars and then 1 star with the same formula `2i - 1`?

## Hint 2

The bottom half is the top-half formula with `i` going **down** from `n - 1` to 1. `range(n - 1, 0, -1)` gives
`n - 1, n - 2, ..., 1`. For `n = 1` it is empty, which is exactly right (no bottom half).

## Hint 3

```
read n
for i from 1 up to n:
    print (n - i) spaces + (2i - 1) stars
for i from n - 1 down to 1:
    print (n - i) spaces + (2i - 1) stars
```
