q = int(input())
for _ in range(q):
    a, b = (int(x) for x in input().split())
    x, y = a, b
    while y:
        x, y = y, x % y
    print(a // x * b)
