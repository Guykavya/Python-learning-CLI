q = int(input())
for _ in range(q):
    n = int(input())
    parts = []
    i = 2
    while i * i <= n:
        if n % i == 0:
            e = 0
            while n % i == 0:
                n //= i
                e += 1
            parts.append(f"{i}^{e}")
        i += 1
    if n > 1:
        parts.append(f"{n}^1")
    print(" ".join(parts) if parts else "1")
