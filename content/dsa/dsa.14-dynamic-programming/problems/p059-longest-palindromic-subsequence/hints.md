## Hint 1

Fill the table of chapter section 17 first:

- `s[i] == s[j]`: `f[i][j] = f[i + 1][j - 1] + 2` (the inside is 0 when it is empty);
- otherwise: `f[i][j] = max(f[i + 1][j], f[i][j - 1])`, dropping one end;
- `f[i][i] = 1`.

Fill by **length** of the range, short ranges first.

## Hint 2

Now walk from `i = 0`, `j = n - 1`, building two lists: `left` (letters for the front) and `right` (letters for the back).

- `s[i] == s[j]` and `i < j`: append `s[i]` to both, then `i += 1`, `j -= 1`.
- `i == j`: a single middle letter; remember it and stop.
- ends differ: move toward the bigger of `f[i + 1][j]` and `f[i][j - 1]` (`i += 1` or `j -= 1`).

## Hint 3

```
left, right, middle = [], [], ""
i, j = 0, n - 1
while i <= j:
    if i == j: middle = s[i]; break
    if s[i] == s[j]: left.append(s[i]); right.append(s[j]); i += 1; j -= 1
    elif f[i + 1][j] >= f[i][j - 1]: i += 1
    else: j -= 1
return "".join(left) + middle + "".join(reversed(right))
```
