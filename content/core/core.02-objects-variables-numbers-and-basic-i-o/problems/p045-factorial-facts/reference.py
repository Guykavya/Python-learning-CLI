import math

n = int(input())
f = math.factorial(n)
print("Digits:", int(math.log10(f)) + 1)
print("Trailing zeros:", n // 5 + n // 25 + n // 125 + n // 625)
