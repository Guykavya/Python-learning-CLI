from fractions import Fraction

amount = Fraction(input())
have = int(input())
want = int(input())
scaled = amount * want / have
print(f"Cups: {scaled}")
print(f"About: {float(scaled):.3f}")
