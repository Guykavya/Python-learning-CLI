## Hint 1

Linear search is easy: the count is the position of the target (1 for the value 1, 37 for 37), or 100 if it is
missing, because the loop then runs to the end.

## Hint 2

For binary search keep a table with columns `lo`, `hi`, `mid`, `a[mid]`. For target 1: (0, 99, 49, 50), then
`hi = 48`: (0, 48, 24, 25), and so on.

## Hint 3

For 101, every `a[mid]` is smaller, so `lo` keeps moving right: the middles are 50, 75, 88, 94, 97, 99, 100, and then
`lo > hi`. `found` stays `False`.
