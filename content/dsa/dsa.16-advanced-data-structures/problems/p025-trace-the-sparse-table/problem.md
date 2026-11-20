# Trace the sparse table

The sparse table for minimum (chapter section 15), built and then queried three times. Ranges are half-open. Predict **exactly** what this program prints. Do not run it.

```python
a = [5, 2, 4, 7, 6, 3, 1, 8]
n = len(a)
table = [a[:]]
k = 1
while (1 << k) <= n:
    prev, half = table[-1], 1 << (k - 1)
    table.append([min(prev[i], prev[i + half]) for i in range(n - (1 << k) + 1)])
    k += 1
for k, row in enumerate(table):
    print(k, row)
lg = [0] * (n + 1)
for i in range(2, n + 1):
    lg[i] = lg[i // 2] + 1
for l, r in [(1, 7), (3, 6), (2, 3)]:
    k = lg[r - l]
    print(l, r, "k =", k, "blocks at", l, r - (1 << k), "->", min(table[k][l], table[k][r - (1 << k)]))
```

Write your answer in `answer.txt`, one printed line per line: four table rows, then three query lines.

## How to work

1. Row 0 is the array. Row `k` has `n - 2**k + 1` entries; entry `i` is the minimum of two entries of row `k - 1`: `i` and `i + 2**(k - 1)`.
2. `lg[L]` is the floor of `log2(L)`: `lg[1] = 0`, `lg[2] = lg[3] = 1`, `lg[4..7] = 2`.
3. For each query: `k = lg[r - l]`, the blocks start at `l` and at `r - 2**k`; take the minimum of the two entries of row `k`.

## After you answer

1. Check each query answer against the slice of the array directly.
2. In which query do the two blocks overlap, and in which are they the same block?
3. How many entries does the table hold in total? Compare with `n * log2(n)`.
