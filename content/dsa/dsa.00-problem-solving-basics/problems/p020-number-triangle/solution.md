## Approach

The outer loop chooses the row `i` from 1 to `n`. For each row, the inner loop goes from 1 to `i`
and builds the row as a string. A space is added **before** every number except the first, so there
is never a space at the start or the end. Then the finished row is printed. When `n` is 0, `range(1, 1)`
is empty and nothing is printed.

## Trace

Input `3`:

| i | j | line after this step |
|---|---|---|
| 1 | 1 | `"1"` -> printed |
| 2 | 1 | `"1"` |
| 2 | 2 | `"1 2"` -> printed |
| 3 | 1 | `"1"` |
| 3 | 2 | `"1 2"` |
| 3 | 3 | `"1 2 3"` -> printed |

## Code

```python
n = int(input())

for i in range(1, n + 1):
    line = ""
    for j in range(1, i + 1):
        if j > 1:
            line += " "
        line += str(j)
    print(line)
```

## Complexity

The rows have 1, 2, ..., n numbers, so the total work is 1 + 2 + ... + n = n(n+1)/2, which is O(n^2).

## Another way

**Print as you go with `end`.** Inside the inner loop, `print(j, end=" ")`, and after the inner loop a plain
`print()` to finish the line. This is shorter, but every line then ends with an invisible trailing space.
Many checkers ignore trailing spaces (this one does), but some do not. Building the string, or printing
`" "` only when `j > 1`, gives exactly the requested output and is the safer habit.

## Edge cases

- `n = 0`: no rows at all, so no output.
- `n = 1`: a single line `1`.
- Numbers with two digits (row 10 onward) need no special handling: the separator is always one space.
