from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
price = Decimal(input())
qty = int(input())
rate = Decimal(input())
subtotal = (price * qty).quantize(CENT, rounding=ROUND_HALF_UP)
tax = (subtotal * rate / 100).quantize(CENT, rounding=ROUND_HALF_UP)
total = subtotal + tax
print(f"Subtotal: {subtotal}")
print(f"Tax: {tax}")
print(f"Total: {total}")
