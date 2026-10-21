## Walkthrough

Each row is one pass of a `while` loop. The `print` happens with the values at the start of the row.

**Loop 1** (`a = 252`, `b = 105`):

| `a` | `b` | printed | `a % b` | new `a`, `b` |
|---|---|---|---|---|
| 252 | 105 | `252 105` | 42 | 105, 42 |
| 105 | 42 | `105 42` | 21 | 42, 21 |
| 42 | 21 | `42 21` | 0 | 21, 0 |
| 21 | 0 | loop stops | | |

Then `gcd 21` is printed.

**Loop 2** (`a = 17`, `b = 5`):

| `a` | `b` | printed | `a % b` | new `a`, `b` |
|---|---|---|---|---|
| 17 | 5 | `17 5` | 2 | 5, 2 |
| 5 | 2 | `5 2` | 1 | 2, 1 |
| 2 | 1 | `2 1` | 0 | 1, 0 |
| 1 | 0 | loop stops | | |

Then `gcd 1`: 17 and 5 share no divisor except 1.

**Loop 3** (`a = 18`, `b = 48`):

| `a` | `b` | printed | `a % b` | new `a`, `b` |
|---|---|---|---|---|
| 18 | 48 | `18 48` | 18 | 48, 18 |
| 48 | 18 | `48 18` | 12 | 18, 12 |
| 18 | 12 | `18 12` | 6 | 12, 6 |
| 12 | 6 | `12 6` | 0 | 6, 0 |
| 6 | 0 | loop stops | | |

Then `gcd 6`.

Full output:

```
252 105
105 42
42 21
gcd 21
17 5
5 2
2 1
gcd 1
18 48
48 18
18 12
12 6
gcd 6
```

## Key idea

- The remainder `a % b` is always smaller than `b`, so `b` keeps shrinking and must reach 0. The loop always stops.
- `a, b = b, a % b` uses the **old** values on the right side. Writing `a = b` then `b = a % b` would be wrong,
  because the second line would see the new `a`.
- If `a < b`, then `a % b == a`, so the first step just swaps the two numbers. You do not need an `if` to put
  the bigger number first.
- The gcd never changes from step to step, so the last non-zero value is the gcd of the original pair.
