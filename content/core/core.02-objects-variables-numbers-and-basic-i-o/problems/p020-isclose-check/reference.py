import math

a = float(input())
b = float(input())
c = float(input())
print("Exact:", a + b == c)
print("Close:", math.isclose(a + b, c, abs_tol=1e-9))
