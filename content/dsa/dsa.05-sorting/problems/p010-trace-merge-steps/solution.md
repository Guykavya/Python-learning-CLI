## Approach

Follow the pointers. Each loop round takes exactly one value and prints one line, so the first call prints 5 lines (the leftover then adds 9 and 10), the second prints none, the third prints 2 lines.

## Expected output

```text
out = [1] i = 1 j = 0
out = [1, 2] i = 1 j = 1
out = [1, 2, 4] i = 2 j = 1
out = [1, 2, 4, 4] i = 2 j = 2
out = [1, 2, 4, 4, 7] i = 3 j = 2
[1, 2, 4, 4, 7, 9, 10]
[3]
out = [1] i = 0 j = 1
out = [1, 2] i = 0 j = 2
[1, 2, 5, 6]
```

## Why

The first call takes 1, 2, 4 (left), 4 (right), 7, and then appends 9, 10. The third call takes 1 and 2 from `right`, then `right` is exhausted and `[5, 6]` is appended. A merge of sizes `n` and `m` makes at most `n + m - 1` comparisons.
