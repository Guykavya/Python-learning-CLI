sales = {}
for _ in range(int(input())):
    city, item, qty = input().split()
    inner = sales.setdefault(city, {})
    inner[item] = inner.get(item, 0) + int(qty)
for city in sorted(sales):
    print(f"{city}: {sum(sales[city].values())}")
    for item in sorted(sales[city]):
        print(f"  {item} {sales[city][item]}")
