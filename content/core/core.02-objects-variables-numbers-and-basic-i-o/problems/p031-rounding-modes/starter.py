from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

text = input()
print(f"float round: {round(float(text), 2):.2f}")
print(f"half up: {round(float(text), 2):.2f}")
print(f"half even: {round(float(text), 2):.2f}")
