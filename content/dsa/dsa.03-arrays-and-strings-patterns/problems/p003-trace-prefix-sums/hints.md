## Hint 1

The first `add` line: `p` is `[0]`, `x = 3`, so the new last box is `0 + 3`. The next box adds `-1` to that.
Notice that `print` inside the loop runs **after** `append`, so `p[-1]` is the new box.

## Hint 2

For `(2, 5)` the program reads `p[5]` and `p[1]`. `p[5]` is the total of all five elements; `p[1]` is just the first one.

## Hint 3

The list is `[0, 3, 2, 6, 7, 12]`. Index carefully: `p[3]` is the fourth box.
