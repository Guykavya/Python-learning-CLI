## Code

```python
name = input()
qty = int(input())
price = float(input())
print(f"{name:<15.15}{qty:>4}{price:>9.2f}{qty * price:>11,.2f}")
```

## Reading the specs

- `<15.15`: left-align in width 15, and cut to at most 15 characters.
- `>4`: right-align in 4.
- `>9.2f`: right-align in 9, two decimals.
- `>11,.2f`: right-align in 11, thousands separators, two decimals.

## Another way

`name[:15].ljust(15)` does the same as `<15.15`. Slicing is safe even for short names because slices never fail.
