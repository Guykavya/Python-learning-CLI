# Fuel cost calculator (buggy). Fix it so it matches the specification.
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
distance = int(input())
mileage = float(input())
price = Decimal(float(input()))
litres = distance * mileage
cost = Decimal(litres) * price
print("Litres:", round(litres, 2))
print("Cost:", cost.quantize(CENT), sep="")
