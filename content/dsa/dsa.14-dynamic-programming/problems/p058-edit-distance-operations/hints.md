## Hint 1

Build the full table `f[i][j]` of p057 (you need all of it to walk back). Then stand at `(len(a), len(b))` and ask which neighbour produced the value:

- `a[i-1] == b[j-1]` and `f[i][j] == f[i-1][j-1]`: keep the character, go to `(i-1, j-1)`, no operation;
- `f[i][j] == f[i-1][j-1] + 1`: replace `a[i-1]` by `b[j-1]`, go to `(i-1, j-1)`;
- `f[i][j] == f[i-1][j] + 1`: delete `a[i-1]`, go to `(i-1, j)`;
- otherwise: insert `b[j-1]`, go to `(i, j-1)`.

Check `i > 0` and `j > 0` before you read `a[i-1]` or `f[i-1][...]`. Keep going `while i > 0 or j > 0`.

## Hint 2

Positions. At `(i, j)` the part of the string to the **right** of `a[:i]` is already finished (it equals `b[j:]`), and the left part `a[:i]` has not been touched. So `a[i-1]` is still at position `i - 1`: delete and replace use `i - 1`. An insert puts `b[j-1]` right after `a[:i]`: position `i`. Because every later operation is at a position `<=` this one, nothing to its left has moved. So emit the operations **in the order you find them**, and do **not** reverse the list.

## Hint 3

```
ops = []; i, j = n, m
while i > 0 or j > 0:
    if i > 0 and j > 0 and a[i-1] == b[j-1] and f[i][j] == f[i-1][j-1]:
        i -= 1; j -= 1
    elif i > 0 and j > 0 and f[i][j] == f[i-1][j-1] + 1:
        ops.append(("replace", i - 1, b[j-1])); i -= 1; j -= 1
    elif i > 0 and f[i][j] == f[i-1][j] + 1:
        ops.append(("delete", i - 1)); i -= 1
    else:
        ops.append(("insert", i, b[j-1])); j -= 1
return ops
```
