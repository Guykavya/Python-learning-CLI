## Hint 1

Slices never raise errors. Out-of-range bounds are trimmed to fit. Write the indices: a0 b1 c2 d3 e4 f5.

## Hint 2

With a positive step, if start is not left of stop, the slice is empty. With a negative step, start must be to the right of stop, and a missing start means "the last character".

## Hint 3

`s[::-1][1:3]` happens in two steps: reverse first, then slice the reversed string.
