## Hint 1

Which format spec types give fixed-point, percent and scientific notation?

## Hint 2

`,` adds thousands separators, `.2f` fixes two decimals, `%` multiplies by 100 and adds a percent sign, `e` is scientific, and `+` forces a sign.

## Hint 3

```
x = float(input())
print(f"{x:,.2f}")
print(f"{x:.1%}")
print(f"{x:.3e}")
print(f"{x:+.1f}")
```
