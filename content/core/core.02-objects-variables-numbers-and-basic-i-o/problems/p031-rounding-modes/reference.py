from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

text = input()
cent = Decimal("0.01")
print(f"float round: {round(float(text), 2):.2f}")
print(f"half up: {Decimal(text).quantize(cent, rounding=ROUND_HALF_UP)}")
print(f"half even: {Decimal(text).quantize(cent, rounding=ROUND_HALF_EVEN)}")
