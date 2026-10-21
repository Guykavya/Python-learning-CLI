name = input()
qty = int(input())
price = float(input())
print(f"{name:<15.15}{qty:>4}{price:>9.2f}{qty * price:>11,.2f}")
