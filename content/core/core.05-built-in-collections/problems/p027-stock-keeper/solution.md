## Approach

A dict maps each item to its quantity. `get(item, 0)` treats unknown items as zero, so `add`,
`sell` and `check` all work the same way for new and existing items.

## Code

```python
stock = {}
while True:
    parts = input().split()
    if parts[0] == "end":
        break
    if parts[0] == "add":
        item, n = parts[1], int(parts[2])
        stock[item] = stock.get(item, 0) + n
    elif parts[0] == "sell":
        item, n = parts[1], int(parts[2])
        have = stock.get(item, 0)
        if n > have:
            print(f"Cannot sell {n} {item}: only {have} left")
        else:
            stock[item] = have - n
    elif parts[0] == "check":
        print(f"{parts[1]}: {stock.get(parts[1], 0)}")
print("Stock:")
in_stock = [item for item in sorted(stock) if stock[item] > 0]
if not in_stock:
    print("(nothing in stock)")
for item in in_stock:
    print(item, stock[item])
```

## Complexity

Each command is O(1) on average. The final report sorts k items: O(k log k).
