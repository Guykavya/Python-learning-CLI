## Hint 1

Width alone never cuts. Which part of a format spec cuts a string?

## Hint 2

For a string, precision is a maximum length: `{name:<15.15}` pads to 15 and also cuts at 15. For numbers use `>9.2f` and `>11,.2f`.

## Hint 3

```
name = input()
qty = int(input())
price = float(input())
print(f"{name:<15.15}{qty:>4}{price:>9.2f}{qty * price:>11,.2f}")
```
