## Hint 1

Keep four boundaries: `top`, `bottom`, `left`, `right`. Each side you walk moves one boundary
inward.

## Hint 2

Loop while `top <= bottom and left <= right`. Walk the top row, then `top += 1`; the right
column, then `right -= 1`; and so on.

## Hint 3

Before walking the bottom row and the left column, check again that `top <= bottom` and
`left <= right`, or a single remaining row or column is printed twice.
