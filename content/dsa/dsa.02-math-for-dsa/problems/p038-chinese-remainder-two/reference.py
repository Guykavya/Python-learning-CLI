def ext(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext(b, a % b)
    return g, y1, x1 - (a // b) * y1


q = int(input())
for _ in range(q):
    a1, m1, a2, m2 = [int(x) for x in input().split()]
    g, u, v = ext(m1, m2)
    if (a2 - a1) % g != 0:
        print(-1)
    else:
        m2g = m2 // g
        k = (a2 - a1) // g * u % m2g
        print(a1 + m1 * k)
