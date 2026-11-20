## Hint 1

Start from `lcs_table(a, b)` (section 14). The walk of `lcs_string` goes from `(len(a), len(b))` to the edge. In `lcs_string`, a step up (`i -= 1`) **drops** `a[i-1]`. In a supersequence nothing may be dropped. So what must you append before each step up? Before each step left?

## Hint 2

Follow the larger neighbour, exactly as `lcs_string` does: that keeps the walk on a path where the LCS letters are shared. When `i` or `j` reaches 0, the walk of `lcs_string` stops, but here the remaining letters of the other string must still be written. You collect the letters from the end backwards, so reverse at the end.

## Hint 3

```
f = lcs table of a and b
i, j = len(a), len(b); out = []
while i > 0 and j > 0:
    if a[i-1] == b[j-1]:  out.append(a[i-1]); i -= 1; j -= 1     # shared letter, once
    elif f[i-1][j] >= f[i][j-1]:  out.append(a[i-1]); i -= 1     # a's letter is not in the LCS here
    else:  out.append(b[j-1]); j -= 1
while i > 0: out.append(a[i-1]); i -= 1
while j > 0: out.append(b[j-1]); j -= 1
return "".join(reversed(out))
```
