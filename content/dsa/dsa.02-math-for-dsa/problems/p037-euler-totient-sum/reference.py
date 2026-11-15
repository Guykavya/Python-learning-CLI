LIMIT = 10 ** 6
spf = list(range(LIMIT + 1))
for i in range(2, LIMIT + 1):
    if i * i > LIMIT:
        break
    if spf[i] == i:
        for m in range(i * i, LIMIT + 1, i):
            if spf[m] == m:
                spf[m] = i

q = int(input())
for _ in range(q):
    n = int(input())
    phi = 1
    total = 1
    while n > 1:
        p = spf[n]
        e = 0
        pe1 = 1
        while n % p == 0:
            n //= p
            e += 1
            if e > 1:
                pe1 *= p
        phi *= pe1 * (p - 1)
        total *= pe1 * (e * (p - 1) + p)
    print(phi, total)
