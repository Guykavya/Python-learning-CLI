## Approach

A dict of dicts mirrors the question "for this city, for this item, how many?". `setdefault`
creates each inner dict the first time a city appears.

## Code

```python
sales = {}
for _ in range(int(input())):
    city, item, qty = input().split()
    inner = sales.setdefault(city, {})
    inner[item] = inner.get(item, 0) + int(qty)
for city in sorted(sales):
    print(f"{city}: {sum(sales[city].values())}")
    for item in sorted(sales[city]):
        print(f"  {item} {sales[city][item]}")
```

## Complexity

O(n) to build; sorting k cities and their items for output.
