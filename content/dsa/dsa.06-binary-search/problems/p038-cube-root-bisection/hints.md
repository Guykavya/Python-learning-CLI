## Hint 1

Which interval is guaranteed to contain `x`? For `c` up to `10^15`, how large can `x` be? (Think: `x^3 <= x^3 + x = c`.)

## Hint 2

`x <= c^(1/3) <= 10^5`, so `[0, 100000]` is safe. The predicate `mid^3 + mid >= c` is False...False True...True: if it is True, `hi = mid`, else `lo = mid`. No `+ 1`: on real numbers there is no gap between neighbours.

## Hint 3

```
lo, hi = 0.0, 100000.0
for _ in range(100):
    mid = (lo + hi) / 2
    if mid * mid * mid + mid >= c: hi = mid
    else: lo = mid
print(f"{(lo + hi) / 2:.6f}")
```
