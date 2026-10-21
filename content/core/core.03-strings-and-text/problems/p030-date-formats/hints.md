## Hint 1

Split the date into its three parts. Then, which slice of `"JanFebMar..."` holds month number `m`?

## Hint 2

Each month name is 3 characters. Month 1 is at 0 to 3, month 2 at 3 to 6, so month `m` is at `3 * (m - 1)` to `3 * m`.

## Hint 3

```
y, m, d = input().strip().split("-")
y, m, d = int(y), int(m), int(d)
months = "JanFebMarAprMayJunJulAugSepOctNovDec"
print(f"{d:02}/{m:02}/{y}")
print(f"{d} {months[3 * (m - 1):3 * m]} {y}")
print(f"{y}{m:02}{d:02}")
```
