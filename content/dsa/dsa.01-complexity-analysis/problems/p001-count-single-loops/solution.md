## Walkthrough

| counter | values the loop variable takes | count |
|---|---|---|
| `a` | 0, 1, ..., 19 | 20 |
| `b` | 0, 3, 6, 9, 12, 15, 18 | 7 |
| `c` | 5, 6, ..., 20 (that is 20 - 5 + 1 values) | 16 |
| `d` | 1, 3, 5, ..., 19 (odd numbers up to 20) | 10 |
| `e` | 20 passes, plus 1 more for i = 0, 4, 8, 12, 16 | 25 |

Output:

```
a 20
b 7
c 16
d 10
e 25
```

## General formulas

- `a = n`.
- `b = ceil(n / 3)`, which is `(n + 2) // 3`.
- `c = n - 4` (for `n >= 5`).
- `d = ceil(n / 2)`, which is `(n + 1) // 2`.
- `e = n + ceil(n / 4)`.

## Key idea

Every one of these counters is proportional to `n`: doubling `n` roughly doubles each count. The step (3 or 2),
the starting value (5), or an extra `if` inside change the constant in front of `n`, not the shape of the growth.
That is why all five loops are O(n).
