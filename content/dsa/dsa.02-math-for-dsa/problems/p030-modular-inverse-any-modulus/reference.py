def ext(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext(b, a % b)
    return g, y1, x1 - (a // b) * y1


q = int(input())
for _ in range(q):
    a, m = [int(x) for x in input().split()]
    a %= m
    g, x, y = ext(a, m)
    if g != 1:
        print(-1)
    else:
        print(x % m)
