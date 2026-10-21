## Approach

Treat each row as three pieces, each produced by its own small loop:

1. **Spaces:** `n - i` of them, so the last row (`i = n`) has none and the rows line up in the middle.
2. **Rising part:** values `1, 2, ..., i`, which is `range(1, i + 1)`.
3. **Falling part:** values `i - 1, ..., 1`, which is `range(i - 1, 0, -1)`. It starts at `i - 1`
   so that the peak `i` is written once.

Each value is written as `v % 10`, its last digit, so every value takes exactly one character and the
triangle keeps its shape. Build the row as a string, then print it once, which also guarantees there
are no trailing spaces.

## Trace

Input `n = 3`:

| i | spaces | rising v values | falling v values | line printed |
|---|---|---|---|---|
| 1 | 2 | 1 | (none) | `  1` |
| 2 | 1 | 1, 2 | 1 | ` 121` |
| 3 | 0 | 1, 2, 3 | 2, 1 | `12321` |

## Code

```python
n = int(input())

for i in range(1, n + 1):
    line = " " * (n - i)
    # Going up: 1, 2, ..., i
    for v in range(1, i + 1):
        line += f"{v % 10}"
    # Coming down: i - 1, ..., 1
    for v in range(i - 1, 0, -1):
        line += f"{v % 10}"
    print(line)
```

## Complexity

Row `i` has about `n + i` characters, so the total output is about `1.5 * n * n` characters:
O(n^2) time, which is the size of the output itself. Memory is one row at a time, O(n).

## Another way

**One loop per row using distance from the centre.** Row `i` has `2i - 1` digits. For position `j`
from 1 to `2i - 1`, the value is `i - abs(i - j)`: it rises to `i` at the middle and falls again.
That replaces the two inner loops with one and is the idea behind many symmetric patterns (diamonds,
hourglasses). Two loops are easier to read; the distance formula is easier to adapt.

## Edge cases

- `n = 1`: one row, `1`, with no spaces.
- `n >= 10`: values 10, 11, ... are written as 0, 1, ...; row 10's peak is `0`.
