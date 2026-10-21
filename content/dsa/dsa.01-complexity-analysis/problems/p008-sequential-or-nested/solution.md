## Walkthrough

| block | counting | total |
|---|---|---|
| sequential | 8 + 8 | 16 |
| nested | 8 * 8 | 64 |
| nested constant | 8 * (1 + 5) | 48 |
| shrinking | 8 + 4 + 2 + 1 | 15 |

Output:

```
sequential 16
nested 64
nested constant 48
shrinking 15
```

## Big-O for general n

- Sequential: `n + n = 2n`, O(n).
- Nested: `n * n`, O(n^2).
- Nested constant: `6n`, O(n). The inner loop has a fixed length.
- Shrinking: `n + n/2 + n/4 + ... + 1`, which is less than `2n`. O(n), even though a loop sits inside a loop.

## Key idea

Do not decide the complexity by looking at the indentation. Add up how many times the innermost line really
runs. A halving outer loop with an inner loop of length `size` gives a sum that halves each time, and such a
sum is at most twice its first term.
