## Approach

The loop variable `i` runs from 1 to `k`. `n` stays fixed. On each step, build the line with an f-string so the
spacing is exact. Negative numbers and zero need no special handling: `-4 * 2` is `-8` and the f-string prints the minus sign.

## Trace

Input `7` then `3`.

| Iteration | `i` | `n * i` | Printed |
|---|---|---|---|
| 1 | 1 | 7 | `7 x 1 = 7` |
| 2 | 2 | 14 | `7 x 2 = 14` |
| 3 | 3 | 21 | `7 x 3 = 21` |

## Code

```python
n = int(input())
k = int(input())
for i in range(1, k + 1):
    print(f"{n} x {i} = {n * i}")
```

## Complexity

`k` lines, each a constant amount of work: O(k).

## Another way

Use `print` with several values, which puts one space between them by default:

```python
print(n, "x", i, "=", n * i)
```

This gives the same output. Or keep a running product instead of multiplying: start `p = 0` and do `p += n`
on each step. That replaces multiplication with addition, which is how tables were built by hand. The f-string
version is the clearest; reach for the running total only when each step genuinely depends on the previous one.
