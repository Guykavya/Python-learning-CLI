price = float(input())
qty = int(input())
rate = float(input())
subtotal = price * qty
tax = subtotal * rate / 100
print(f"Subtotal: {subtotal:.2f}")
print(f"Tax: {tax:.2f}")
print(f"Total: {subtotal + tax:.2f}")
