# Fuel cost calculator (fixed).
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
distance = Decimal(input())
mileage = Decimal(input())
price = Decimal(input())
litres = distance / mileage
cost = litres * price
print("Litres:", litres.quantize(CENT, rounding=ROUND_HALF_UP))
print("Cost:", cost.quantize(CENT, rounding=ROUND_HALF_UP))
