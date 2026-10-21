## Approach

Look at the shape row by row and count. For `n = 4`:

| row `i` | spaces | stars |
|---|---|---|
| 1 | 3 | 1 |
| 2 | 2 | 3 |
| 3 | 1 | 5 |
| 4 | 0 | 7 |

Spaces are `n - i` and stars are `2 * i - 1`. So one loop over the rows is enough. Each row is
`" " * (n - i) + "*" * (2 * i - 1)`. Nothing is added after the stars, so there are no trailing spaces.

## Trace

For `n = 3`:

| `i` | `n - i` | `2 * i - 1` | printed line |
|---|---|---|---|
| 1 | 2 | 1 | `  *` |
| 2 | 1 | 3 | ` ***` |
| 3 | 0 | 5 | `*****` |

## Code

```python
n = int(input())
for i in range(1, n + 1):
    print(" " * (n - i) + "*" * (2 * i - 1))
```

## Complexity

There are `n` rows and the longest has `2n - 1` characters, so the total output is about `n * n`
characters: O(n^2). That is the size of the picture itself, so you cannot do better.

## Another way

Use nested loops with `print(..., end="")`: an inner loop prints the spaces one at a time, a second
inner loop prints the stars, then a plain `print()` ends the line. This is what you would do in a
language without string repetition. In Python the repetition version is shorter and harder to get wrong.

## Edge cases

- `n = 0`: `range(1, 1)` is empty, so nothing is printed.
- `n = 1`: one row, 0 spaces and 1 star.
