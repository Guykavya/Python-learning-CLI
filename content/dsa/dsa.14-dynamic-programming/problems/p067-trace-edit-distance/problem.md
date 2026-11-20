# Trace edit distance

The edit-distance table of chapter section 15, for `"kitten"` and `"sitting"`. Predict **exactly** what this program prints. Do not run it until you have written your answer.

```python
def edit_table(a, b):
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
    return f

a, b = "kitten", "sitting"
f = edit_table(a, b)
for i, row in enumerate(f):
    label = a[i - 1] if i > 0 else "-"
    print(label, " ".join(str(v) for v in row))
print("distance:", f[len(a)][len(b)])
```

Write your answer in `answer.txt`: one line per row of the table (7 lines; the first starts with `-`, the others with a letter of `"kitten"`), then the `distance:` line.

## How to work

1. Draw a grid with 7 rows (`""`, `k`, `i`, `t`, `t`, `e`, `n`) and 8 columns (`""`, `s`, `i`, `t`, `t`, `i`, `n`, `g`).
2. Fill row 0 with `0 1 2 ... 7` and column 0 with `0 1 ... 6`: the base cases (insert `j` letters, delete `i` letters).
3. Fill the rest row by row, left to right. For each cell ask one question: **are the two letters equal?**
   - Equal: copy the cell diagonally up-left.
   - Different: `1 +` the smallest of up-left, up, left.
4. Check each row before the next one: neighbouring cells never differ by more than 1.

## Example of one cell

Cell `f[2][2]` (row `i`, column `i`): the letters are equal, so it copies `f[1][1] = 1`. Cell `f[1][1]` (`k` against `s`): different, `1 + min(0, 1, 1) = 1`.

## After you answer

1. Which cells copy their diagonal? Mark them. Do they line up along one path?
2. The distance is 3. Which three operations does the path from the corner back to `f[0][0]` give?
3. Why can no row contain both a `1` and a `3` side by side?
