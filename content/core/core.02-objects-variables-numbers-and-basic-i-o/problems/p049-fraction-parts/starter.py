from fractions import Fraction

f = Fraction(input())
print("floor:", int(f))
print("remainder:", f - int(f))
print("truncated:", int(f))
print("rounded:", int(f + Fraction(1, 2)))
print("check:", int(f) + (f - int(f)) == f)
