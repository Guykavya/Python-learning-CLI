a = int(input())
b = input().strip()
m = int(input())

r = 1 % m
for ch in b:
    d = int(ch)
    r = pow(r, 10, m) * pow(a, d, m) % m
print(r)
