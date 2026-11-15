def ext(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext(b, a % b)
    return g, y1, x1 - (a // b) * y1


q = int(input())
for _ in range(q):
    a, b, m = [int(x) for x in input().split()]
    a %= m
    b %= m
    g, x0, y0 = ext(a, m)
    if b % g != 0:
        print(-1)
    else:
        m2 = m // g
        print(x0 * (b // g) % m2)
