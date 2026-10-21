## Hint 1

`zip` gives pairs of characters until the shorter line runs out. What does it do with the
leftover characters?

## Hint 2

After the `zip` loop, the leftover is the part of the longer string starting at position
`len(shorter)`.

## Hint 3

`a[len(b):] + b[len(a):]`: one of the two slices is always empty. Why?
