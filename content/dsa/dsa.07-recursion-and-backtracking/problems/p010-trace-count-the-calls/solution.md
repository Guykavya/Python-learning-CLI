## Approach

The call order is a preorder walk of the recursion tree: root, left sub-tree, right sub-tree. Build it from small pieces: `calls(2) = [2, 1, 0]`, `calls(3) = [3] + calls(2) + [1]`, `calls(4) = [4] + calls(3) + calls(2)`, `calls(5) = [5] + calls(4) + calls(3)`.

## Expected output

```text
5
15
[5, 4, 3, 2, 1, 0, 1, 2, 1, 0, 3, 2, 1, 0, 1]
3 5 3
```

## Why

`calls(3)` = `[3, 2, 1, 0, 1]` (5 calls), `calls(4)` = `[4, 3, 2, 1, 0, 1, 2, 1, 0]` (9 calls), so `calls(5)` = `[5]` + 9 + 5 = 15 calls.
`fib(3)` runs twice and `fib(2)` three times, although each value only needs to be computed once. With a memo, `fib(5)` needs only 6 distinct calls (5, 4, 3, 2, 1, 0) plus a few look-ups. This repeated work is why the plain version grows exponentially (`fib(30)` makes 2,692,537 calls).
