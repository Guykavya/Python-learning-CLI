## Hint 1

First fill the full LCS table `f` (p055); you need **all** of it, not two rows, because you will walk back through it. Then start at the corner `(len(a), len(b))` and walk towards `(0, 0)`, collecting characters.

## Hint 2

At `(i, j)`: if `a[i-1] == b[j-1]`, that character is in the answer: record it and move diagonally to `(i-1, j-1)`. Otherwise move to the neighbour with the larger value: up `(i-1, j)` if `f[i-1][j] >= f[i][j-1]`, else left `(i, j-1)`. That neighbour has the same value as `f[i][j]`, so no length is lost. Stop when `i` or `j` reaches 0.

## Hint 3

You collect the characters from the **end** backwards, so reverse them at the end.

```
i, j = n, m; out = []
while i > 0 and j > 0:
    if a[i-1] == b[j-1]: out.append(a[i-1]); i -= 1; j -= 1
    elif f[i-1][j] >= f[i][j-1]: i -= 1
    else: j -= 1
return "".join(reversed(out))
```
