q = int(input())
for _ in range(q):
    a, b, m = (int(x) for x in input().split())
    result = 1 % m
    base = a % m
    while b > 0:
        if b % 2 == 1:
            result = result * base % m
        base = base * base % m
        b //= 2
    print(result)
