q = int(input())
for _ in range(q):
    a, b = (int(x) for x in input().split())
    while b != 0:
        a, b = b, a % b
    print(a)
