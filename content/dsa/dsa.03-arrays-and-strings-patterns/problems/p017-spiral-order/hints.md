## Hint 1

After walking the top row, which row is the new `top`? After walking the right column, which column is the new
`right`? Draw a 3 x 4 grid and shade each side as you walk it.

## Hint 2

The loop runs while `top <= bottom and left <= right`. Walk the top row and do `top += 1`; walk the right column and
do `right -= 1`. The bottom row only exists if `top <= bottom` is **still** true, and the left column only if
`left <= right` is still true: check again before those two sides.

## Hint 3

```
top, bottom, left, right = 0, r - 1, 0, c - 1
while top <= bottom and left <= right:
    for col in left..right:          take g[top][col]
    top += 1
    for row in top..bottom:          take g[row][right]
    right -= 1
    if top <= bottom:
        for col in right down to left: take g[bottom][col]
        bottom -= 1
    if left <= right:
        for row in bottom down to top: take g[row][left]
        left += 1
```
