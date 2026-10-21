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
