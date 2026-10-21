n = int(input())

if n == 1:
    total = 0
else:
    total = 1  # 1 divides every n > 1; its partner n is not a proper divisor

d = 2
while d * d <= n:
    if n % d == 0:
        total += d
        partner = n // d
        if partner != d:
            total += partner
    d += 1

if total == n:
    print("perfect")
elif total > n:
    print("abundant")
else:
    print("deficient")
