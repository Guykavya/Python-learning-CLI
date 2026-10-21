## Approach

Reuse what you know. The top half is the pyramid: row `i` is `n - i` spaces and `2i - 1` stars.
The bottom half is the same rows in reverse order, starting one below the middle. So use the **same formula**
with `i` running from `n - 1` down to 1. Starting at `n - 1` (not `n`) is what stops the middle row being printed twice.

## Trace

For `n = 3`:

| loop | `i` | spaces `n - i` | stars `2i - 1` | printed |
|---|---|---|---|---|
| top | 1 | 2 | 1 | `  *` |
| top | 2 | 1 | 3 | ` ***` |
| top | 3 | 0 | 5 | `*****` |
| bottom | 2 | 1 | 3 | ` ***` |
| bottom | 1 | 2 | 1 | `  *` |

## Code

```python
n = int(input())
for i in range(1, n + 1):
    print(" " * (n - i) + "*" * (2 * i - 1))
for i in range(n - 1, 0, -1):
    print(" " * (n - i) + "*" * (2 * i - 1))
```

## Complexity

`2n - 1` rows of at most `2n - 1` characters: O(n^2), the size of the picture.

## Another way

One loop over `r` from `-(n - 1)` to `n - 1` with `k = n - abs(r)`: row `r` has `n - k` spaces and `2k - 1` stars.
`abs(r)` is the distance from the middle row, which makes the symmetry explicit and needs no second loop.
It is neat, but harder to read. Prefer the two-loop version unless the shape has several symmetric parts.

## Edge cases

- `n = 0`: both ranges are empty, nothing printed.
- `n = 1`: top loop prints `*`, bottom loop `range(0, 0, -1)` is empty. Only one row.
- `n = 30`: 59 rows, widest is 59 stars.
