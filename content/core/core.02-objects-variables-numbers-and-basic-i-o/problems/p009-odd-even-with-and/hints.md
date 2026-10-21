## Hint 1

In binary, what does the last bit of an odd number always look like?

## Hint 2

`n & 1` keeps only the last bit, so it is `1` for odd numbers and `0` for even ones.
Compare it with `1` to get a `bool`.

## Hint 3

Careful with precedence: `&` binds **less** tightly than `==`. Write `(n & 1) == 1`.
