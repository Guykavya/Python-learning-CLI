p = float(input())
r = float(input())
t = int(input())
n = int(input())
a = p * (1 + r / 100 * n) ** n * t
print(f"Amount: {a:.2f}")
print(f"Interest: {a - p:.2f}")
