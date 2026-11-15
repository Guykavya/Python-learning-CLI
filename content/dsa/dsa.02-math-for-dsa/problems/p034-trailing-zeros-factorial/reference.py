q = int(input())
for _ in range(q):
    n, p = [int(x) for x in input().split()]
    total = 0
    while n > 0:
        n //= p
        total += n
    print(total)
