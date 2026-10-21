## Walkthrough for n = 6

| `i` | `a` inner runs | `b` inner runs (range(i)) | `c` inner runs (range(i, 6)) | `d` inner runs |
|---|---|---|---|---|
| 0 | 6 | 0 | 6 | 3 |
| 1 | 6 | 1 | 5 | 3 |
| 2 | 6 | 2 | 4 | 3 |
| 3 | 6 | 3 | 3 | 3 |
| 4 | 6 | 4 | 2 | 3 |
| 5 | 6 | 5 | 1 | 3 |
| total | 36 | 15 | 21 | 18 |

## Formulas

- `a = n * n`
- `b = 0 + 1 + ... + (n - 1) = n * (n - 1) / 2`
- `c = n + (n - 1) + ... + 1 = n * (n + 1) / 2`
- `d = 3 * n`

For `n = 1000`: `a = 1000000`, `b = 499500`, `c = 500500`, `d = 3000`.

Output:

```
6 36 15 21 18
1000 1000000 499500 500500 3000
```

## Key idea

`a`, `b` and `c` are all O(n^2). The "triangle" loops `b` and `c` do about half the work of the full square,
but half of `n^2` is still `n^2` times a constant. `d` has two nested loops but is only O(n), because the inner
loop has a fixed length. Nesting alone does not make code quadratic: what matters is how long each loop is.
Notice also that `b + c = a + n`; can you see why from the table?
