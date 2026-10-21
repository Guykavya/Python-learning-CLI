## Approach

Two dicts keyed by item: `qty` and `price`. Every command is a dict lookup or update. The two
listings are decorate-sort-undecorate with tuple keys: `(qty, name)` for low stock and
`(-value, name)` for the report.

## Code

```python
qty = {}
price = {}
revenue = 0
while True:
    parts = input().split()
    match parts:
        case ["end"]:
            break
        case ["stock", item, n, p]:
            qty[item] = qty.get(item, 0) + int(n)
            price[item] = int(p)
            print(f"Stocked {item}: {qty[item]}")
        case ["sell", item, n]:
            n = int(n)
            if item not in qty:
                print(f"Unknown item {item}")
            elif qty[item] < n:
                print(f"Not enough {item} (have {qty[item]})")
            else:
                qty[item] -= n
                revenue += n * price[item]
                print(f"Sold {n} {item} for {n * price[item]}")
        case ["low", limit]:
            low = sorted((q, item) for item, q in qty.items() if q < int(limit))
            if not low:
                print("No low stock")
            for q, item in low:
                print(item, q)
        case ["report"]:
            rows = sorted((-qty[i] * price[i], i) for i in qty)
            for neg, item in rows:
                print(f"{item} {qty[item]} x {price[item]} = {-neg}")
            print("Total value:", sum(qty[i] * price[i] for i in qty))
print("Revenue:", revenue)
```

## Complexity

`stock` and `sell` are O(1) on average. `low` and `report` are O(n log n).
