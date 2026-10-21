from fractions import Fraction

f = Fraction(input())
whole = f // 1
rest = f % 1
print("floor:", whole)
print("remainder:", rest)
print("truncated:", int(f))
print("rounded:", round(f))
print("check:", whole + rest == f)
