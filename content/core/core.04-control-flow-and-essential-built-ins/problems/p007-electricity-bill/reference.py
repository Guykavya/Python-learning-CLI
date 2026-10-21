units = int(input())
if units < 0:
    print("invalid")
else:
    if units <= 100:
        energy = units * 3.00
    elif units <= 200:
        energy = 300 + (units - 100) * 4.50
    elif units <= 500:
        energy = 300 + 450 + (units - 200) * 6.00
    else:
        energy = 300 + 450 + 1800 + (units - 500) * 8.00
    fixed = 50 if units <= 200 else 100
    print(f"Energy: {energy:.2f}")
    print(f"Fixed: {fixed:.2f}")
    print(f"Total: {energy + fixed:.2f}")
