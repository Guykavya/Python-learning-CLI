import math

n = int(input())
f = math.factorial(n)
print("Digits:", len(str(f)))
print("Trailing zeros:", n // 5)
