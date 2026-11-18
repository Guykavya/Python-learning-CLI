## Approach

Fill the edit-distance table (p057), then walk back from the corner and read off which move produced each cell (chapter section 15). The new part is the **positions**.

At cell `(i, j)` during the walk, the characters of `a` after index `i - 1` have already been dealt with: the string now looks like `a[:i] + b[j:]`. The untouched prefix `a[:i]` starts at position 0, so:

- delete or replace `a[i-1]`: position `i - 1`;
- insert `b[j-1]` in front of the finished part `b[j:]`: position `i`.

The walk only moves left, so every later operation is at a position `<=` the current one, and an operation at position `p` never moves a character at a position `< p`. That is why the operations can be applied **in the order the walk finds them**, right to left, without any position adjustments.

```python
def edit_ops(a, b):
    n, m = len(a), len(b)
    f = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        f[i][0] = i
    for j in range(m + 1):
        f[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                f[i][j] = f[i - 1][j - 1]
            else:
                f[i][j] = 1 + min(f[i - 1][j - 1], f[i - 1][j], f[i][j - 1])
    ops = []
    i, j = n, m
    while i > 0 or j > 0:              # right to left: positions on the left never move
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] and f[i][j] == f[i - 1][j - 1]:
            i, j = i - 1, j - 1                          # keep, no operation
        elif i > 0 and j > 0 and f[i][j] == f[i - 1][j - 1] + 1:
            ops.append(("replace", i - 1, b[j - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and f[i][j] == f[i - 1][j] + 1:
            ops.append(("delete", i - 1))
            i -= 1
        else:
            ops.append(("insert", i, b[j - 1]))           # right after a[:i]
            j -= 1
    return ops
```

The order of the tests matters (chapter section 15): the "keep" test comes first and checks that the characters are equal, so two equal characters are never "replaced" at a cost of 1. Each operation found lowers `f[i][j]` by exactly 1 and the walk ends at `f[0][0] = 0`, so there are exactly `f[n][m]` operations.

## Complexity

`O(n * m)` time and space for the table, `O(n + m)` for the walk.

## Another way

Walk back as above, reverse the list (left to right, like the chapter's `edit_script`), and then fix the positions: keep a running `shift` (+1 after an insert, -1 after a delete) and add it to every position computed from the original indices. Both versions are correct; the right-to-left order needs no bookkeeping at all, which is why it is the one used here.
